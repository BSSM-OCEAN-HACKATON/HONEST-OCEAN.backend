from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import JSONResponse
import shutil
import os
import json
import tempfile
from app.services.analysis_service import analyze_with_gemini, analyze_with_gpt
from app.services.market_price_service import get_market_price
from app.schemas import ResponseModel, SeafoodStats
from typing import Optional

router = APIRouter()

@router.post("/analyze", response_model=ResponseModel)
async def analyze_fish(
    image: UploadFile = File(...),
    fishLength: Optional[float] = Form(None),
):
    try:
        # Save uploaded file randomly to handle concurrency somewhat safely in simple use cases, 
        # or just use a temp file.
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(image.filename)[1]) as temp_file:
            shutil.copyfileobj(image.file, temp_file)
            temp_path = temp_file.name

        try:
            openai_key = os.environ.get("OPENAI_API_KEY")
            gemini_key = os.environ.get("GEMINI_API_KEY")
            
            # Prioritize OpenAI if available (or change logic if user prefers Gemini)
            # The user request implies checking existence.
            # If ONLY one is present, use it. If both, pick one.
            # Let's check keys.
            
            result_str = None
            
            if openai_key and openai_key.strip():
                result_str = analyze_with_gpt(temp_path, openai_key, fish_length=fishLength)
            elif gemini_key and gemini_key.strip():
                result_str = analyze_with_gemini(temp_path, gemini_key, fish_length=fishLength)
            else:
                 raise HTTPException(status_code=500, detail="No API Key (OpenAI or Gemini) configured on server")
            
            clean_result = result_str.replace("```json", "").replace("```", "").strip()
            
            try:
                data = json.loads(clean_result)
                # Map snake_case or whatever the LLM returned to our schema
                # We requested specific keys in the prompt: seafoodType, marketPrice, estimatedWeight
                # If LLM followed instructions, data is compatible with SeafoodStats

                if data.get("is_fish") is False:
                    # Return 400 Bad Request if not a fish
                    raise HTTPException(status_code=400, detail="Not a fish or seafood")
                
                # Fetch Real Market Price
                if "seafoodType" in data:
                    fish_name = data["seafoodType"]
                    unit_price_per_kg = await get_market_price(fish_name)
                    
                    est_weight_val = None
                    if "estimatedWeight" in data:
                         try:
                             est_weight_val = float(data["estimatedWeight"])
                         except (ValueError, TypeError):
                             pass

                    if unit_price_per_kg is not None and est_weight_val is not None:
                         total_price = unit_price_per_kg * est_weight_val
                         data["marketPrice"] = int(total_price)
                    
                    # Check Regulations
                    from app.services.regulation_service import check_regulation
                    
                    fl_val = None
                    if fishLength is not None:
                        try:
                            fl_val = float(fishLength)
                        except (ValueError, TypeError):
                            pass
                            
                    reg_result = check_regulation(fish_name, length_cm=fl_val, weight_kg=est_weight_val)
                    data["currentlyForbidden"] = reg_result["forbidden"]
                
                return {
                    "status": "success",
                    "data": data
                }
            except json.JSONDecodeError:
                # Fallback if JSON fails
                return {
                    "status": "error",
                    "data": {"raw_output": result_str}
                }

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "data": {"message": str(e)}
        }
@router.post("/compare_fillet")
async def compare_fillet(
    image1: UploadFile = File(...),
    image2: UploadFile = File(...),
    length1: int = Form(...),
    length2: int = Form(...),
):
    try:
        res1 = await _analyze_single_fish(image1, float(length1))
        res2 = await _analyze_single_fish(image2, float(length2))
        
        fw1 = res1.get("filletWeights", 0.0)
        fw2 = res2.get("filletWeights", 0.0)
        
        max_idx = 0 if fw1 >= fw2 else 1
        max_weight_kg = fw1 if fw1 >= fw2 else fw2
        
        # portion is 200g based. input weight is kg.
        portion = int((max_weight_kg * 1000) / 200)
        
        return {
            "fishes": [res1, res2],
            "maxFIsh": max_idx,
            "portion": portion
        }
    except HTTPException:
         raise
    except Exception as e:
         import traceback
         traceback.print_exc()
         raise HTTPException(status_code=500, detail=str(e))

async def _analyze_single_fish(image: UploadFile, length_val: float) -> dict:
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(image.filename)[1]) as temp_file:
            shutil.copyfileobj(image.file, temp_file)
            temp_path = temp_file.name

        openai_key = os.environ.get("OPENAI_API_KEY")
        gemini_key = os.environ.get("GEMINI_API_KEY")
        
        result_str = None
        if openai_key and openai_key.strip():
            result_str = analyze_with_gpt(temp_path, openai_key, fish_length=length_val)
        elif gemini_key and gemini_key.strip():
            result_str = analyze_with_gemini(temp_path, gemini_key, fish_length=length_val)
        else:
             raise HTTPException(status_code=500, detail="No API Key configured")
        
        clean_result = result_str.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_result)
        
        if data.get("is_fish") is False:
            raise HTTPException(status_code=400, detail="Not a fish or seafood")
        
        # Ensure calculated fields
        if "seafoodType" in data:
            fish_name = data["seafoodType"]
            
            # Market Price
            unit_price_per_kg = await get_market_price(fish_name)
            est_weight_val = None
            if "estimatedWeight" in data:
                 try:
                     est_weight_val = float(data["estimatedWeight"])
                 except (ValueError, TypeError):
                     pass
            
            if unit_price_per_kg is not None and est_weight_val is not None:
                 total_price = unit_price_per_kg * est_weight_val
                 data["marketPrice"] = int(total_price)
            
            # Regulations
            from app.services.regulation_service import check_regulation
            reg_result = check_regulation(fish_name, length_cm=length_val, weight_kg=est_weight_val)
            data["currentlyForbidden"] = reg_result["forbidden"]
            
            # Fillet Yield
            from app.services.fish_data import get_fillet_yield
            yield_rate = get_fillet_yield(fish_name)
            if est_weight_val:
                fillet_weight = est_weight_val * yield_rate
                data["filletWeights"] = round(fillet_weight, 2)
            else:
                 data["filletWeights"] = 0.0

        return data

    except Exception:
        raise
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

@router.get("/test")
async def get_mock_test_data(
    id: Optional[str] = Query(None, description="1=고등어, 2=게, 3=대문어(금지체장 걸리게)")
):
    if id == "1":
        return {
            "seafoodType": "고등어",
            "marketPrice": 30000,
            "estimatedWeight": 0.5,
            "currentlyForbidden": False
        }
    elif id == "2":
         return {
            "seafoodType": "꽃게",
            "marketPrice": 25000,
            "estimatedWeight": 0.4,
            "currentlyForbidden": False
        }
    elif id == "3":
         return {
            "seafoodType": "대문어",
            "marketPrice": 50000,
            "estimatedWeight": 0.5,
            "currentlyForbidden": True
        }
    else:
        # Default fallback (same as case 1)
        return {
            "seafoodType": "고등어",
            "marketPrice": 30000,
            "estimatedWeight": 0.5,
            "currentlyForbidden": False
        }

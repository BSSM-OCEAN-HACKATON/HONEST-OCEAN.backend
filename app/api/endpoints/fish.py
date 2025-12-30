from fastapi import APIRouter, UploadFile, File, Form, HTTPException
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

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "data": {"message": str(e)}
        }

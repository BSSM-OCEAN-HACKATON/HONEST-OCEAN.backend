from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from app.schemas import ResponseModel, Record, RecordDataResponse
from typing import List, Optional
from app.database import get_db
from app.models import MerchantRecord
from app.services.storage_service import upload_file

router = APIRouter()

@router.post("/record", response_model=ResponseModel)
async def create_merchant_record(
    image: UploadFile = File(...),
    seafoodType: str = Form(...),
    marketPrice: int = Form(...),
    estimatedWeight: float = Form(...),
    merchantWeight: float = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # Upload Image to Supabase Storage
        file_content = await image.read()
        image_url = await upload_file(file_content, image.filename, image.content_type)
        
        new_record = MerchantRecord(
            seafood_type=seafoodType,
            market_price=marketPrice,
            estimated_weight=estimatedWeight,
            merchant_weight=merchantWeight,
            latitude=latitude,
            longitude=longitude,
            image_filename=image_url # Storing URL in the filename column
        )
        
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        
        return {
            "status": "success",
            "data": {
                "recordId": new_record.id,
                "msg": "success"
            }
        }
    except Exception as e:
        print(f"Error creating record: {e}")
        return {
            "status": "error",
            "data": {"message": str(e)}
        }

from app.schemas import ResponseModel, Record, RecordDataResponse, RecordDetail

# ... (imports remain)

@router.get("/records", response_model=RecordDetail)
async def get_merchant_record_detail(
    id: str = Query(..., description="Record ID"),
    db: Session = Depends(get_db)
):
    try:
        record_id_int = int(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    record = db.query(MerchantRecord).filter(MerchantRecord.id == record_id_int).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    return {
        "recordId": str(record.id),
        "image": record.image_filename if record.image_filename else "",
        "merchantWeight": str(record.merchant_weight),
        "data": {
            "location": {
                "latitude": record.latitude,
                "longitude": record.longitude
            }
        },
        "stats": {
            "seafoodType": record.seafood_type,
            "marketPrice": record.market_price,
            "estimatedWeight": record.estimated_weight
        }
    }


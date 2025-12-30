from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base

class MerchantRecord(Base):
    __tablename__ = "merchant_records"

    id = Column(Integer, primary_key=True, index=True)
    seafood_type = Column(String, index=True)
    market_price = Column(Integer)
    estimated_weight = Column(Float)
    merchant_weight = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    image_filename = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

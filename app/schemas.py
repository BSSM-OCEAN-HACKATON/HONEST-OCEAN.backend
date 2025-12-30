from pydantic import BaseModel
from typing import List, Optional

class Location(BaseModel):
    latitude: float
    longitude: float

class DataLocation(BaseModel):
    location: Location

class SeafoodStats(BaseModel):
    seafoodType: str
    marketPrice: int
    estimatedWeight: float
    currentlyForbidden: Optional[bool] = None

class Record(BaseModel):
    recordId: int
    msg: str

class RecordDetail(BaseModel):
    recordId: str
    image: str
    merchantWeight: str
    data: DataLocation
    stats: SeafoodStats

class RecordDataResponse(BaseModel):
    record: List[RecordDetail]

class ResponseModel(BaseModel):
    status: str
    data: dict

class PathRequest(BaseModel):
    points: List[int]

class PathResponse(BaseModel):
    points: List[int]

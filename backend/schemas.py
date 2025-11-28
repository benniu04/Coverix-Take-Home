from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class MessageCreate(BaseModel):
    content: str


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    timestamp: datetime

    class Config:
        from_attributes = True


class VehicleResponse(BaseModel):
    id: int
    vin: Optional[str] = None
    year: Optional[int] = None
    make: Optional[str] = None
    body_type: Optional[str] = None
    vehicle_use: Optional[str] = None
    blind_spot_warning: Optional[bool] = None
    days_per_week: Optional[int] = None
    one_way_miles: Optional[int] = None
    annual_mileage: Optional[int] = None

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    id: int
    session_id: str
    current_state: str
    zip_code: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    license_type: Optional[str] = None
    license_status: Optional[str] = None
    messages: List[MessageResponse] = []
    vehicles: List[VehicleResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    session_id: str
    response: str
    current_state: str
    is_complete: bool


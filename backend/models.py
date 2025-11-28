from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from database import Base


class VehicleUse(str, enum.Enum):
    COMMUTING = "commuting"
    COMMERCIAL = "commercial"
    FARMING = "farming"
    BUSINESS = "business"


class LicenseType(str, enum.Enum):
    FOREIGN = "foreign"
    PERSONAL = "personal"
    COMMERCIAL = "commercial"


class LicenseStatus(str, enum.Enum):
    VALID = "valid"
    SUSPENDED = "suspended"


class ConversationState(str, enum.Enum):
    ZIP_CODE = "zip_code"
    FULL_NAME = "full_name"
    EMAIL = "email"
    VEHICLE_CHOICE = "vehicle_choice"  # VIN or Year/Make/Body
    VEHICLE_VIN = "vehicle_vin"
    VEHICLE_YEAR = "vehicle_year"
    VEHICLE_MAKE = "vehicle_make"
    VEHICLE_BODY = "vehicle_body"
    VEHICLE_USE = "vehicle_use"
    BLIND_SPOT_WARNING = "blind_spot_warning"
    COMMUTE_DAYS = "commute_days"
    COMMUTE_MILES = "commute_miles"
    ANNUAL_MILEAGE = "annual_mileage"
    ADD_ANOTHER_VEHICLE = "add_another_vehicle"
    LICENSE_TYPE = "license_type"
    LICENSE_STATUS = "license_status"
    COMPLETE = "complete"


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), unique=True, index=True)
    current_state = Column(String(50), default=ConversationState.ZIP_CODE.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # User info
    zip_code = Column(String(10), nullable=True)
    full_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    license_type = Column(String(20), nullable=True)
    license_status = Column(String(20), nullable=True)
    
    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    vehicles = relationship("Vehicle", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String(20))  # 'user' or 'assistant'
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="messages")


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    
    # Vehicle identification (either VIN or Year/Make/Body)
    vin = Column(String(17), nullable=True)
    year = Column(Integer, nullable=True)
    make = Column(String(100), nullable=True)
    body_type = Column(String(100), nullable=True)
    
    # Vehicle details
    vehicle_use = Column(String(20), nullable=True)
    blind_spot_warning = Column(Boolean, nullable=True)
    
    # Commuting details (if vehicle_use is commuting)
    days_per_week = Column(Integer, nullable=True)
    one_way_miles = Column(Integer, nullable=True)
    
    # Commercial/Farming/Business details
    annual_mileage = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="vehicles")


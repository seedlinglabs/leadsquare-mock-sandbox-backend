from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class RecurrenceFrequency(str, Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"


class RecurrencePattern(BaseModel):
    frequency: RecurrenceFrequency
    interval: int = 1
    days_of_week: Optional[List[str]] = None
    start_date: str
    end_date: str


class LeadInfo(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None

    class Config:
        from_attributes = True


class AppointmentBase(BaseModel):
    lead_id: int
    title: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    duration_minutes: int = 30
    timezone: str = "UTC"
    is_recurring: bool = False
    recurrence_pattern: Optional[Dict[str, Any]] = None

    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v, info):
        if 'start_date' in info.data and v <= info.data['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

    @field_validator('duration_minutes')
    @classmethod
    def validate_duration(cls, v):
        if v <= 0:
            raise ValueError('duration_minutes must be positive')
        return v


class AppointmentCreate(AppointmentBase):
    pass


class RecurringAppointmentCreate(BaseModel):
    lead_id: int
    title: str
    description: Optional[str] = None
    start_time: str  # Format: "HH:MM"
    end_time: str  # Format: "HH:MM"
    timezone: str = "UTC"
    is_recurring: bool = True
    recurrence_pattern: RecurrencePattern


class AppointmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    timezone: Optional[str] = None
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None


class AppointmentResponse(BaseModel):
    id: int
    lead: LeadInfo
    title: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    duration_minutes: int
    timezone: str
    is_recurring: bool
    recurrence_pattern: Optional[Dict[str, Any]] = None
    status: AppointmentStatus
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

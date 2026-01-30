from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from enum import Enum


class LeadStatus(str, Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"


class LeadSource(str, Enum):
    WEBSITE = "website"
    REFERRAL = "referral"
    SOCIAL_MEDIA = "social_media"
    EMAIL_CAMPAIGN = "email_campaign"
    COLD_CALL = "cold_call"
    TRADE_SHOW = "trade_show"
    OTHER = "other"


class LeadBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    mobile: Optional[str] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    website: Optional[str] = None
    street_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    source: Optional[LeadSource] = LeadSource.WEBSITE
    description: Optional[str] = None
    notes: Optional[str] = None


class LeadCreate(LeadBase):
    owner_id: Optional[int] = None


class LeadUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    website: Optional[str] = None
    street_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    status: Optional[LeadStatus] = None
    source: Optional[LeadSource] = None
    lead_score: Optional[int] = None
    estimated_value: Optional[int] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    owner_id: Optional[int] = None
    last_contacted_at: Optional[datetime] = None


class LeadResponse(LeadBase):
    id: int
    status: LeadStatus
    lead_score: int
    estimated_value: Optional[int] = None
    owner_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_contacted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

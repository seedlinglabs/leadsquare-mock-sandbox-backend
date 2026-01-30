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


class PaginationInfo(BaseModel):
    page: int
    limit: int
    total: int
    totalPages: int


class LeadsListResponse(BaseModel):
    success: bool = True
    data: list[LeadResponse]
    pagination: PaginationInfo


class LeadDetailResponse(BaseModel):
    success: bool = True
    data: LeadResponse


class LeadCreateResponse(BaseModel):
    success: bool = True
    message: str = "Lead created successfully"
    data: LeadResponse


class LeadUpdateResponse(BaseModel):
    success: bool = True
    message: str = "Lead updated successfully"
    data: LeadResponse


class LeadDeleteResponse(BaseModel):
    success: bool = True
    message: str = "Lead deleted successfully"


class LeadStatusUpdateRequest(BaseModel):
    status: LeadStatus


class LeadStatusUpdateResponse(BaseModel):
    success: bool = True
    message: str = "Lead status updated"
    data: LeadResponse


class BulkLeadCreate(BaseModel):
    leads: list[LeadCreate]


class BulkLeadCreateResponse(BaseModel):
    success: bool = True
    message: str
    created: int
    failed: int


class BulkLeadDelete(BaseModel):
    ids: list[int]


class BulkLeadDeleteResponse(BaseModel):
    success: bool = True
    message: str

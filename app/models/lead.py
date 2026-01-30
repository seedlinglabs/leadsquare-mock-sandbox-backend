from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum


from app.core.database import Base


class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"


class LeadSource(str, enum.Enum):
    WEBSITE = "website"
    REFERRAL = "referral"
    SOCIAL_MEDIA = "social_media"
    EMAIL_CAMPAIGN = "email_campaign"
    COLD_CALL = "cold_call"
    TRADE_SHOW = "trade_show"
    OTHER = "other"


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)

    # Contact Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)
    email = Column(String(255), index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    mobile = Column(String(20), nullable=True)

    # Company Information
    company_name = Column(String(255), nullable=True)
    job_title = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    company_size = Column(String(50), nullable=True)
    website = Column(String(255), nullable=True)

    # Address
    street_address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)

    # Lead Details
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW, nullable=False)
    source = Column(Enum(LeadSource), default=LeadSource.WEBSITE, nullable=True)
    lead_score = Column(Integer, default=0)
    estimated_value = Column(Integer, nullable=True)

    # Notes and Description
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Tracking
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_contacted_at = Column(DateTime(timezone=True), nullable=True)

    owner = relationship("User", back_populates="leads")

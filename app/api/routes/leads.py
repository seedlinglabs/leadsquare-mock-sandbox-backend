from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.crud.lead import lead_crud
from app.schemas.lead import (
    LeadCreate,
    LeadUpdate,
    LeadResponse,
    LeadStatus,
    LeadSource,
    LeadsListResponse,
    LeadDetailResponse,
    LeadCreateResponse,
    LeadUpdateResponse,
    LeadDeleteResponse,
    LeadStatusUpdateRequest,
    LeadStatusUpdateResponse,
    BulkLeadCreate,
    BulkLeadCreateResponse,
    BulkLeadDelete,
    BulkLeadDeleteResponse,
)
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=LeadsListResponse)
async def get_leads(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[LeadStatus] = Query(None, description="Filter by lead status"),
    source: Optional[LeadSource] = Query(None, description="Filter by lead source"),
    search: Optional[str] = Query(None, description="Search in name, email, company"),
    sortBy: str = Query("created_at", description="Sort field"),
    sortOrder: str = Query("desc", description="Sort order (asc/desc)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all leads with pagination, filters, and search"""
    result = await lead_crud.get_with_filters(
        db=db,
        page=page,
        limit=limit,
        status=status,
        source=source,
        search=search,
        sort_by=sortBy,
        sort_order=sortOrder,
    )

    return LeadsListResponse(
        success=True,
        data=result["data"],
        pagination=result["pagination"],
    )


@router.get("/{lead_id}", response_model=LeadDetailResponse)
async def get_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get single lead by ID"""
    lead = await lead_crud.get(db, lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Lead not found",
                },
            },
        )
    return LeadDetailResponse(success=True, data=lead)


@router.post("/", response_model=LeadCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    lead_data: LeadCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new lead"""
    # Check if lead with email already exists
    existing_lead = await lead_crud.get_by_email(db, lead_data.email)
    if existing_lead:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "success": False,
                "error": {
                    "code": "CONFLICT",
                    "message": "Lead with this email already exists",
                },
            },
        )

    lead = await lead_crud.create(db, lead_data)
    return LeadCreateResponse(
        success=True,
        message="Lead created successfully",
        data=lead,
    )


@router.put("/{lead_id}", response_model=LeadUpdateResponse)
async def update_lead(
    lead_id: int,
    lead_data: LeadUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update existing lead"""
    lead = await lead_crud.update(db, lead_id, lead_data)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Lead not found",
                },
            },
        )
    return LeadUpdateResponse(
        success=True,
        message="Lead updated successfully",
        data=lead,
    )


@router.delete("/{lead_id}", response_model=LeadDeleteResponse)
async def delete_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete lead"""
    deleted = await lead_crud.delete(db, lead_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Lead not found",
                },
            },
        )
    return LeadDeleteResponse(
        success=True,
        message="Lead deleted successfully",
    )


@router.patch("/{lead_id}/status", response_model=LeadStatusUpdateResponse)
async def update_lead_status(
    lead_id: int,
    request: LeadStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update lead status only"""
    lead = await lead_crud.update_status(db, lead_id, request.status)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Lead not found",
                },
            },
        )
    return LeadStatusUpdateResponse(
        success=True,
        message="Lead status updated",
        data=lead,
    )


@router.post("/bulk", response_model=BulkLeadCreateResponse, status_code=status.HTTP_201_CREATED)
async def bulk_create_leads(
    request: BulkLeadCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Bulk create leads (CSV import)"""
    result = await lead_crud.bulk_create(db, request.leads)

    return BulkLeadCreateResponse(
        success=True,
        message=f"{result['created']} leads created successfully",
        created=result["created"],
        failed=result["failed"],
    )


@router.delete("/bulk", response_model=BulkLeadDeleteResponse)
async def bulk_delete_leads(
    request: BulkLeadDelete,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Bulk delete leads"""
    deleted = await lead_crud.bulk_delete(db, request.ids)

    return BulkLeadDeleteResponse(
        success=True,
        message=f"{deleted} leads deleted successfully",
    )

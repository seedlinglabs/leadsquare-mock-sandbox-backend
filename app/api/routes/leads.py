from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.crud.lead import lead_crud
from app.schemas.lead import LeadCreate, LeadUpdate, LeadResponse, LeadStatus

router = APIRouter()


@router.post("/", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(lead_data: LeadCreate, db: AsyncSession = Depends(get_db)):
    return await lead_crud.create(db, lead_data)


@router.get("/", response_model=List[LeadResponse])
async def get_leads(
    skip: int = 0,
    limit: int = 100,
    status: Optional[LeadStatus] = Query(None, description="Filter by lead status"),
    owner_id: Optional[int] = Query(None, description="Filter by owner ID"),
    db: AsyncSession = Depends(get_db),
):
    return await lead_crud.get_all(db, skip=skip, limit=limit, status=status, owner_id=owner_id)


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: int, db: AsyncSession = Depends(get_db)):
    lead = await lead_crud.get(db, lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )
    return lead


@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: int, lead_data: LeadUpdate, db: AsyncSession = Depends(get_db)
):
    lead = await lead_crud.update(db, lead_id, lead_data)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )
    return lead


@router.patch("/{lead_id}/status", response_model=LeadResponse)
async def update_lead_status(
    lead_id: int,
    status: LeadStatus,
    db: AsyncSession = Depends(get_db),
):
    lead = await lead_crud.update_status(db, lead_id, status)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )
    return lead


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(lead_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await lead_crud.delete(db, lead_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )

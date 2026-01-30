from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.crud.appointment import appointment_crud
from app.crud.lead import lead_crud
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    RecurringAppointmentCreate,
    AppointmentStatus,
)
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=dict)
async def get_appointments(
    lead_id: Optional[int] = Query(None, description="Filter by lead ID"),
    start_date: Optional[str] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    status: Optional[AppointmentStatus] = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all appointments with optional filters"""
    appointments = await appointment_crud.get_all(
        db=db,
        lead_id=lead_id,
        start_date=start_date,
        end_date=end_date,
        status=status,
    )

    return {
        "success": True,
        "data": appointments,
    }


@router.get("/{appointment_id}", response_model=dict)
async def get_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get single appointment by ID"""
    appointment = await appointment_crud.get(db, appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Appointment not found",
                },
            },
        )

    return {
        "success": True,
        "data": appointment,
    }


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment_data: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new appointment"""
    # Verify lead exists
    lead = await lead_crud.get(db, appointment_data.lead_id)
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

    appointment = await appointment_crud.create(db, appointment_data)

    return {
        "success": True,
        "message": "Appointment created successfully",
        "data": appointment,
    }


@router.post("/recurring", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_recurring_appointment(
    recurring_data: RecurringAppointmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create recurring appointments"""
    # Verify lead exists
    lead = await lead_crud.get(db, recurring_data.lead_id)
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

    appointments = await appointment_crud.create_recurring(db, recurring_data)

    return {
        "success": True,
        "message": "Recurring appointments created",
        "count": len(appointments),
        "data": appointments,
    }


@router.put("/{appointment_id}", response_model=dict)
async def update_appointment(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an appointment"""
    appointment = await appointment_crud.update(db, appointment_id, appointment_data)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Appointment not found",
                },
            },
        )

    return {
        "success": True,
        "message": "Appointment updated",
        "data": appointment,
    }


@router.delete("/{appointment_id}", response_model=dict)
async def delete_appointment(
    appointment_id: int,
    delete_series: bool = Query(False, description="Delete entire series for recurring appointments"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an appointment"""
    deleted = await appointment_crud.delete(db, appointment_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Appointment not found",
                },
            },
        )

    return {
        "success": True,
        "message": "Appointment deleted",
    }

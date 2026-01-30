from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from datetime import datetime, timedelta

from app.models.appointment import Appointment, AppointmentStatus
from app.schemas.appointment import (
    AppointmentCreate,
    RecurringAppointmentCreate,
    AppointmentUpdate,
)


class AppointmentCRUD:
    async def create(
        self, db: AsyncSession, appointment_data: AppointmentCreate
    ) -> Appointment:
        appointment = Appointment(**appointment_data.model_dump())
        db.add(appointment)
        await db.commit()
        await db.refresh(appointment)
        return appointment

    async def get(
        self, db: AsyncSession, appointment_id: int
    ) -> Optional[Appointment]:
        result = await db.execute(
            select(Appointment).where(Appointment.id == appointment_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        db: AsyncSession,
        lead_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        status: Optional[AppointmentStatus] = None,
    ) -> List[Appointment]:
        query = select(Appointment)

        if lead_id:
            query = query.where(Appointment.lead_id == lead_id)
        if start_date:
            query = query.where(Appointment.start_date >= start_date)
        if end_date:
            query = query.where(Appointment.end_date <= end_date)
        if status:
            query = query.where(Appointment.status == status)

        result = await db.execute(query)
        return list(result.scalars().all())

    async def update(
        self, db: AsyncSession, appointment_id: int, appointment_data: AppointmentUpdate
    ) -> Optional[Appointment]:
        appointment = await self.get(db, appointment_id)
        if not appointment:
            return None

        update_data = appointment_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(appointment, field, value)

        await db.commit()
        await db.refresh(appointment)
        return appointment

    async def delete(self, db: AsyncSession, appointment_id: int) -> bool:
        appointment = await self.get(db, appointment_id)
        if not appointment:
            return False

        await db.delete(appointment)
        await db.commit()
        return True

    async def create_recurring(
        self, db: AsyncSession, recurring_data: RecurringAppointmentCreate
    ) -> List[Appointment]:
        """Create recurring appointments based on pattern"""
        appointments = []
        pattern = recurring_data.recurrence_pattern

        # Parse dates
        start_date = datetime.strptime(pattern.start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(pattern.end_date, "%Y-%m-%d").date()

        # Parse times
        start_hour, start_minute = map(int, recurring_data.start_time.split(":"))
        end_hour, end_minute = map(int, recurring_data.end_time.split(":"))

        # Generate dates based on frequency
        current_date = start_date
        while current_date <= end_date:
            # Check if this day matches the pattern
            should_create = False

            if pattern.frequency == "Daily":
                should_create = True
            elif pattern.frequency == "Weekly":
                day_name = current_date.strftime("%A")
                if pattern.days_of_week and day_name in pattern.days_of_week:
                    should_create = True
            elif pattern.frequency == "Monthly":
                # Create on the same day of month
                if current_date.day == start_date.day:
                    should_create = True

            if should_create:
                # Create datetime objects
                start_datetime = datetime.combine(
                    current_date,
                    datetime.min.time().replace(hour=start_hour, minute=start_minute),
                )
                end_datetime = datetime.combine(
                    current_date,
                    datetime.min.time().replace(hour=end_hour, minute=end_minute),
                )

                # Calculate duration
                duration_minutes = int((end_datetime - start_datetime).total_seconds() / 60)

                appointment = Appointment(
                    lead_id=recurring_data.lead_id,
                    title=recurring_data.title,
                    description=recurring_data.description,
                    start_date=start_datetime,
                    end_date=end_datetime,
                    duration_minutes=duration_minutes,
                    timezone=recurring_data.timezone,
                    is_recurring=True,
                    recurrence_pattern=pattern.model_dump(),
                    status=AppointmentStatus.SCHEDULED,
                )

                db.add(appointment)
                appointments.append(appointment)

            # Move to next date based on interval
            if pattern.frequency == "Daily":
                current_date += timedelta(days=pattern.interval)
            elif pattern.frequency == "Weekly":
                current_date += timedelta(days=7 * pattern.interval)
            elif pattern.frequency == "Monthly":
                # Move to next month
                if current_date.month == 12:
                    current_date = current_date.replace(
                        year=current_date.year + 1, month=1
                    )
                else:
                    current_date = current_date.replace(month=current_date.month + 1)

        await db.commit()

        # Refresh all appointments
        for appointment in appointments:
            await db.refresh(appointment)

        return appointments


appointment_crud = AppointmentCRUD()

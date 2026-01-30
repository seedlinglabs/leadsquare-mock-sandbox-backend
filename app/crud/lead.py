from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List

from app.models.lead import Lead, LeadStatus
from app.schemas.lead import LeadCreate, LeadUpdate


class LeadCRUD:
    async def create(self, db: AsyncSession, lead_data: LeadCreate) -> Lead:
        lead = Lead(**lead_data.model_dump())
        db.add(lead)
        await db.commit()
        await db.refresh(lead)
        return lead

    async def get(self, db: AsyncSession, lead_id: int) -> Optional[Lead]:
        result = await db.execute(select(Lead).where(Lead.id == lead_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[Lead]:
        result = await db.execute(select(Lead).where(Lead.email == email))
        return result.scalar_one_or_none()

    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: Optional[LeadStatus] = None,
        owner_id: Optional[int] = None,
    ) -> List[Lead]:
        query = select(Lead)

        if status:
            query = query.where(Lead.status == status)
        if owner_id:
            query = query.where(Lead.owner_id == owner_id)

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def update(
        self, db: AsyncSession, lead_id: int, lead_data: LeadUpdate
    ) -> Optional[Lead]:
        lead = await self.get(db, lead_id)
        if not lead:
            return None

        update_data = lead_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(lead, field, value)

        await db.commit()
        await db.refresh(lead)
        return lead

    async def delete(self, db: AsyncSession, lead_id: int) -> bool:
        lead = await self.get(db, lead_id)
        if not lead:
            return False

        await db.delete(lead)
        await db.commit()
        return True

    async def update_status(
        self, db: AsyncSession, lead_id: int, status: LeadStatus
    ) -> Optional[Lead]:
        lead = await self.get(db, lead_id)
        if not lead:
            return None

        lead.status = status
        await db.commit()
        await db.refresh(lead)
        return lead


lead_crud = LeadCRUD()

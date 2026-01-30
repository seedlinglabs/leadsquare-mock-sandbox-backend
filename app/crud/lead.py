from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, desc, asc
from typing import Optional, List, Dict, Any

from app.models.lead import Lead, LeadStatus, LeadSource
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

    async def get_with_filters(
        self,
        db: AsyncSession,
        page: int = 1,
        limit: int = 10,
        status: Optional[LeadStatus] = None,
        source: Optional[LeadSource] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get leads with advanced filtering, search, and pagination"""
        query = select(Lead)

        # Apply filters
        if status:
            query = query.where(Lead.status == status)
        if source:
            query = query.where(Lead.source == source)

        # Apply search
        if search:
            search_filter = or_(
                Lead.first_name.ilike(f"%{search}%"),
                Lead.last_name.ilike(f"%{search}%"),
                Lead.email.ilike(f"%{search}%"),
                Lead.company_name.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Apply sorting
        if hasattr(Lead, sort_by):
            sort_column = getattr(Lead, sort_by)
            if sort_order == "asc":
                query = query.order_by(asc(sort_column))
            else:
                query = query.order_by(desc(sort_column))

        # Apply pagination
        skip = (page - 1) * limit
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        leads = list(result.scalars().all())

        return {
            "data": leads,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "totalPages": (total + limit - 1) // limit,
            },
        }

    async def bulk_create(self, db: AsyncSession, leads_data: List[LeadCreate]) -> Dict[str, int]:
        """Bulk create leads"""
        created = 0
        failed = 0

        for lead_data in leads_data:
            try:
                lead = Lead(**lead_data.model_dump())
                db.add(lead)
                created += 1
            except Exception:
                failed += 1

        await db.commit()

        return {"created": created, "failed": failed}

    async def bulk_delete(self, db: AsyncSession, lead_ids: List[int]) -> int:
        """Bulk delete leads"""
        deleted = 0

        for lead_id in lead_ids:
            lead = await self.get(db, lead_id)
            if lead:
                await db.delete(lead)
                deleted += 1

        await db.commit()

        return deleted

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

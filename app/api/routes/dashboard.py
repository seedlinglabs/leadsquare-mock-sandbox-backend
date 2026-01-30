from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.lead import Lead, LeadStatus, LeadSource
from app.models.user import User

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get dashboard statistics"""

    # Total leads
    total_leads_result = await db.execute(select(func.count(Lead.id)))
    total_leads = total_leads_result.scalar()

    # Total leads from last 30 days for comparison
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_leads_result = await db.execute(
        select(func.count(Lead.id)).where(Lead.created_at >= thirty_days_ago)
    )
    recent_leads = recent_leads_result.scalar()

    # Qualified leads
    qualified_result = await db.execute(
        select(func.count(Lead.id)).where(Lead.status == LeadStatus.QUALIFIED)
    )
    qualified_leads = qualified_result.scalar()

    # In progress leads (contacted, proposal, negotiation)
    in_progress_result = await db.execute(
        select(func.count(Lead.id)).where(
            Lead.status.in_([
                LeadStatus.CONTACTED,
                LeadStatus.PROPOSAL,
                LeadStatus.NEGOTIATION,
            ])
        )
    )
    in_progress = in_progress_result.scalar()

    # Converted leads (won)
    converted_result = await db.execute(
        select(func.count(Lead.id)).where(Lead.status == LeadStatus.WON)
    )
    converted = converted_result.scalar()

    # Total revenue (sum of estimated_value for won leads)
    revenue_result = await db.execute(
        select(func.sum(Lead.estimated_value)).where(Lead.status == LeadStatus.WON)
    )
    total_revenue = revenue_result.scalar() or 0

    # Leads by status
    status_result = await db.execute(
        select(Lead.status, func.count(Lead.id))
        .group_by(Lead.status)
    )
    leads_by_status = {str(status): count for status, count in status_result.all()}

    # Leads by source
    source_result = await db.execute(
        select(Lead.source, func.count(Lead.id))
        .group_by(Lead.source)
    )
    leads_by_source = {str(source): count for source, count in source_result.all()}

    # Calculate percentage changes (mock data for now)
    total_leads_change = "+12%" if recent_leads > 0 else "0%"
    qualified_leads_change = "+8%" if qualified_leads > 0 else "0%"

    return {
        "success": True,
        "data": {
            "total_leads": total_leads,
            "total_leads_change": total_leads_change,
            "qualified_leads": qualified_leads,
            "qualified_leads_change": qualified_leads_change,
            "in_progress": in_progress,
            "converted": converted,
            "total_revenue": total_revenue,
            "leads_by_status": leads_by_status,
            "leads_by_source": leads_by_source,
        },
    }


@router.get("/recent-activity")
async def get_recent_activity(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get recent activities"""

    # Get 10 most recent leads
    result = await db.execute(
        select(Lead)
        .order_by(Lead.created_at.desc())
        .limit(10)
    )
    recent_leads = result.scalars().all()

    activities = []
    for lead in recent_leads:
        # Determine activity type based on status
        if lead.status == LeadStatus.NEW:
            activity_type = "lead_created"
            message = f"New lead added: {lead.first_name} {lead.last_name or ''}"
        elif lead.status == LeadStatus.QUALIFIED:
            activity_type = "status_changed"
            message = f"Lead qualified: {lead.first_name} {lead.last_name or ''}"
        elif lead.status == LeadStatus.WON:
            activity_type = "status_changed"
            message = f"Lead converted: {lead.first_name} {lead.last_name or ''}"
        else:
            activity_type = "status_changed"
            message = f"Lead updated: {lead.first_name} {lead.last_name or ''}"

        activities.append({
            "id": lead.id,
            "type": activity_type,
            "message": message,
            "lead": {
                "id": lead.id,
                "first_name": lead.first_name,
                "last_name": lead.last_name,
                "email": lead.email,
                "status": lead.status,
            },
            "created_at": lead.created_at.isoformat() if lead.created_at else None,
        })

    return {
        "success": True,
        "data": activities,
    }

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_async_db
from app.models.template import VMTemplate
from app.schemas.template import TemplateResponse


router = APIRouter(prefix="/templates")


@router.get("", response_model=List[TemplateResponse])
async def list_templates(
    db: AsyncSession = Depends(get_async_db),
    is_public: bool = True
):
    """List available VM templates"""
    query = select(VMTemplate).where(VMTemplate.is_active == True)
    
    if is_public:
        query = query.where(VMTemplate.is_public == True)
    
    result = await db.execute(query.order_by(VMTemplate.name))
    templates = result.scalars().all()
    
    # Add computed fields
    for template in templates:
        template.cost_per_day = template.cost_per_day
        template.cost_per_month = template.cost_per_month
    
    return templates


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Get template details"""
    result = await db.execute(
        select(VMTemplate).where(VMTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    template.cost_per_day = template.cost_per_day
    template.cost_per_month = template.cost_per_month
    
    return template

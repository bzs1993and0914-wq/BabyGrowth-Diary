from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.connection import async_session
from app.models.milestone import Milestone
from app.models.milestone_category import MilestoneCategory
from app.schemas.milestones import (
    CategoryCreate,
    CategoryResponse,
    MilestoneCreate,
    MilestoneResponse,
)

router = APIRouter(prefix="/milestones", tags=["milestones"])


async def get_db():
    async with async_session() as session:
        yield session


@router.post("/", response_model=MilestoneResponse, status_code=201)
async def create_milestone(data: MilestoneCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(Milestone).where(Milestone.daily_record_id == data.daily_record_id)
    )
    if existing.scalars().first():
        raise HTTPException(
            status_code=409, detail="Milestone already exists for this record"
        )

    milestone = Milestone(
        daily_record_id=data.daily_record_id,
        category_id=data.category_id,
        name=data.name,
        description=data.description,
    )
    db.add(milestone)
    await db.commit()

    result = await db.execute(
        select(Milestone)
        .options(selectinload(Milestone.category))
        .where(Milestone.id == milestone.id)
    )
    milestone = result.scalars().first()
    return _build_milestone_response(milestone)


@router.delete("/{milestone_id}", status_code=204)
async def delete_milestone(milestone_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Milestone).where(Milestone.id == milestone_id))
    milestone = result.scalars().first()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    await db.delete(milestone)
    await db.commit()


@router.get("/categories", response_model=List[CategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(MilestoneCategory).order_by(MilestoneCategory.id)
    )
    return [CategoryResponse.model_validate(c) for c in result.scalars().all()]


@router.post("/categories", response_model=CategoryResponse, status_code=201)
async def create_category(data: CategoryCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(MilestoneCategory).where(MilestoneCategory.name == data.name)
    )
    if existing.scalars().first():
        raise HTTPException(
            status_code=409, detail="Category with this name already exists"
        )

    cat = MilestoneCategory(name=data.name, icon=data.icon, is_preset=False)
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return CategoryResponse.model_validate(cat)


def _build_milestone_response(milestone) -> MilestoneResponse:
    return MilestoneResponse(
        id=milestone.id,
        daily_record_id=milestone.daily_record_id,
        category_id=milestone.category_id,
        name=milestone.name,
        description=milestone.description,
        category_name=milestone.category.name if milestone.category else None,
        category_icon=milestone.category.icon if milestone.category else None,
        created_at=milestone.created_at,
    )

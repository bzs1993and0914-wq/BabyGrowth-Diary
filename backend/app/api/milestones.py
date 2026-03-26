from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_db
from app.models.daily_record import DailyRecord
from app.models.milestone import Milestone
from app.models.milestone_category import MilestoneCategory
from app.models.user import User
from app.schemas.milestones import (
    CategoryCreate,
    CategoryResponse,
    MilestoneCreate,
    MilestoneResponse,
)

router = APIRouter(prefix="/milestones", tags=["milestones"])


@router.post("/", response_model=MilestoneResponse, status_code=201)
async def create_milestone(
    data: MilestoneCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """为指定每日记录创建里程碑（每条记录最多一个，重复返回 409）。"""
    rec_result = await db.execute(
        select(DailyRecord).where(
            DailyRecord.id == data.daily_record_id,
            DailyRecord.user_id == current_user.id,
        )
    )
    if not rec_result.scalars().first():
        raise HTTPException(status_code=404, detail="Daily record not found")

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
async def delete_milestone(
    milestone_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除里程碑，同时校验该里程碑归属于当前用户（防止越权删除）。"""
    result = await db.execute(select(Milestone).where(Milestone.id == milestone_id))
    milestone = result.scalars().first()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    rec_result = await db.execute(
        select(DailyRecord).where(
            DailyRecord.id == milestone.daily_record_id,
            DailyRecord.user_id == current_user.id,
        )
    )
    if not rec_result.scalars().first():
        raise HTTPException(status_code=404, detail="Milestone not found")

    await db.delete(milestone)
    await db.commit()


@router.get("/categories", response_model=List[CategoryResponse])
async def list_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取所有里程碑分类列表（含系统预置分类和用户自定义分类）。"""
    result = await db.execute(
        select(MilestoneCategory).order_by(MilestoneCategory.id)
    )
    return [CategoryResponse.model_validate(c) for c in result.scalars().all()]


@router.post("/categories", response_model=CategoryResponse, status_code=201)
async def create_category(
    data: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建自定义里程碑分类，分类名称在全局唯一（重复返回 409）。"""
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
    """将 ORM 里程碑对象（含关联分类）组装为 MilestoneResponse 响应体。"""
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

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_db
from app.models.daily_record import DailyRecord
from app.models.growth_metric import GrowthMetric
from app.models.user import User
from app.schemas.growth_metrics import GrowthCurveData, GrowthMetricCreate, GrowthMetricResponse

router = APIRouter(prefix="/growth-metrics", tags=["growth-metrics"])


@router.post("/", response_model=GrowthMetricResponse, status_code=201)
async def create_metric(
    data: GrowthMetricCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """为指定每日记录添加一条生长指标（身高/体重/头围）数据。"""
    result = await db.execute(
        select(DailyRecord).where(
            DailyRecord.id == data.daily_record_id,
            DailyRecord.user_id == current_user.id,
        )
    )
    record = result.scalars().first()
    if not record:
        raise HTTPException(status_code=404, detail="Daily record not found")

    metric = GrowthMetric(
        daily_record_id=data.daily_record_id,
        metric_type=data.metric_type,
        value=data.value,
        unit=data.unit,
    )
    db.add(metric)
    await db.commit()
    await db.refresh(metric)

    return GrowthMetricResponse(
        id=metric.id,
        daily_record_id=metric.daily_record_id,
        metric_type=metric.metric_type,
        value=metric.value,
        unit=metric.unit,
        date=record.date,
        created_at=metric.created_at,
    )


@router.get("/", response_model=List[GrowthMetricResponse])
async def list_metrics(
    metric_type: Optional[str] = Query(
        None, pattern=r"^(height|weight|head_circumference)$"
    ),
    date_from: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    date_to: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """列出当前用户的生长指标记录，支持按类型和日期范围过滤，结果按日期升序排列。"""
    query = (
        select(GrowthMetric)
        .join(DailyRecord)
        .where(DailyRecord.user_id == current_user.id)
        .options(selectinload(GrowthMetric.daily_record))
        .order_by(DailyRecord.date)
    )

    if metric_type:
        query = query.where(GrowthMetric.metric_type == metric_type)
    if date_from:
        query = query.where(DailyRecord.date >= date_from)
    if date_to:
        query = query.where(DailyRecord.date <= date_to)

    result = await db.execute(query)
    metrics = result.scalars().all()

    return [
        GrowthMetricResponse(
            id=m.id,
            daily_record_id=m.daily_record_id,
            metric_type=m.metric_type,
            value=m.value,
            unit=m.unit,
            date=m.daily_record.date,
            created_at=m.created_at,
        )
        for m in metrics
    ]


@router.get("/curve", response_model=GrowthCurveData)
async def get_curve(
    metric_type: str = Query(..., pattern=r"^(height|weight|head_circumference)$"),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """返回指定类型生长曲线所需的日期序列和对应数值序列，供前端图表直接使用。"""
    query = (
        select(GrowthMetric)
        .join(DailyRecord)
        .where(
            GrowthMetric.metric_type == metric_type,
            DailyRecord.user_id == current_user.id,
        )
        .options(selectinload(GrowthMetric.daily_record))
        .order_by(DailyRecord.date)
    )
    if date_from:
        query = query.where(DailyRecord.date >= date_from)
    if date_to:
        query = query.where(DailyRecord.date <= date_to)

    result = await db.execute(query)
    metrics = result.scalars().all()

    dates = [m.daily_record.date for m in metrics]
    values = [m.value for m in metrics]
    unit = metrics[0].unit if metrics else None

    return GrowthCurveData(
        dates=dates, values=values, metric_type=metric_type, unit=unit
    )


@router.delete("/{metric_id}", status_code=204)
async def delete_metric(
    metric_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除指定生长指标，并校验其归属于当前用户的记录（防止越权删除）。"""
    result = await db.execute(select(GrowthMetric).where(GrowthMetric.id == metric_id))
    metric = result.scalars().first()
    if not metric:
        raise HTTPException(status_code=404, detail="Growth metric not found")

    rec_result = await db.execute(
        select(DailyRecord).where(
            DailyRecord.id == metric.daily_record_id,
            DailyRecord.user_id == current_user.id,
        )
    )
    if not rec_result.scalars().first():
        raise HTTPException(status_code=404, detail="Growth metric not found")

    await db.delete(metric)
    await db.commit()

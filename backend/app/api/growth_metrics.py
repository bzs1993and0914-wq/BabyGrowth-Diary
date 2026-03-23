from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.connection import async_session
from app.models.daily_record import DailyRecord
from app.models.growth_metric import GrowthMetric
from app.schemas.growth_metrics import GrowthCurveData, GrowthMetricCreate, GrowthMetricResponse

router = APIRouter(prefix="/growth-metrics", tags=["growth-metrics"])


async def get_db():
    async with async_session() as session:
        yield session


@router.post("/", response_model=GrowthMetricResponse, status_code=201)
async def create_metric(data: GrowthMetricCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(DailyRecord).where(DailyRecord.id == data.daily_record_id)
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
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(GrowthMetric)
        .join(DailyRecord)
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
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(GrowthMetric)
        .join(DailyRecord)
        .options(selectinload(GrowthMetric.daily_record))
        .where(GrowthMetric.metric_type == metric_type)
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
async def delete_metric(metric_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GrowthMetric).where(GrowthMetric.id == metric_id))
    metric = result.scalars().first()
    if not metric:
        raise HTTPException(status_code=404, detail="Growth metric not found")
    await db.delete(metric)
    await db.commit()

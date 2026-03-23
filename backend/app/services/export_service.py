from __future__ import annotations

import asyncio
import json
import logging
import uuid
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.config import EXPORT_DIR, VERSION
from app.database.connection import async_session
from app.models.daily_record import DailyRecord
from app.services.storage_manager import resolve_media_path

logger = logging.getLogger(__name__)

_export_tasks: Dict[str, dict] = {}


def get_export_status(export_id: str) -> Optional[dict]:
    return _export_tasks.get(export_id)


async def start_export(
    date_from: Optional[str] = None, date_to: Optional[str] = None
) -> str:
    export_id = str(uuid.uuid4())
    _export_tasks[export_id] = {
        "export_id": export_id,
        "status": "processing",
        "progress": 0.0,
        "file_path": None,
        "error": None,
    }
    asyncio.create_task(_run_export(export_id, date_from, date_to))
    return export_id


async def _run_export(
    export_id: str, date_from: Optional[str], date_to: Optional[str]
) -> None:
    task = _export_tasks[export_id]
    try:
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_path = EXPORT_DIR / f"babygrow_export_{timestamp}.zip"

        async with async_session() as session:
            query = (
                select(DailyRecord)
                .options(
                    selectinload(DailyRecord.media_entries),
                    selectinload(DailyRecord.text_entries),
                    selectinload(DailyRecord.milestone),
                    selectinload(DailyRecord.growth_metrics),
                )
                .order_by(DailyRecord.date)
            )
            if date_from:
                query = query.where(DailyRecord.date >= date_from)
            if date_to:
                query = query.where(DailyRecord.date <= date_to)

            result = await session.execute(query)
            records = list(result.scalars().all())

        total = len(records)
        if total == 0:
            task["status"] = "completed"
            task["progress"] = 100.0
            task["file_path"] = str(zip_path)
            return

        metadata = {
            "app": "BabyGrow",
            "version": VERSION,
            "exported_at": datetime.now().isoformat(),
            "total_records": total,
        }

        await asyncio.to_thread(_write_zip, zip_path, records, metadata, task, total)

        task["status"] = "completed"
        task["progress"] = 100.0
        task["file_path"] = str(zip_path)
    except Exception as e:
        logger.exception("Export failed")
        task["status"] = "failed"
        task["error"] = str(e)


def _write_zip(
    zip_path: Path,
    records: list,
    metadata: dict,
    task: dict,
    total: int,
) -> None:
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "metadata.json", json.dumps(metadata, ensure_ascii=False, indent=2)
        )
        zf.writestr(
            "README.txt",
            "BabyGrow Export\n"
            "===============\n\n"
            "This archive contains your baby growth timeline data.\n"
            "- metadata.json: Export metadata\n"
            "- media/: Media files organized by date\n"
            "- records.json: All record data\n",
        )

        records_data: List[dict] = []
        for i, record in enumerate(records):
            rec: dict = {
                "date": record.date,
                "texts": [
                    {"content": t.content, "sort_order": t.sort_order}
                    for t in record.text_entries
                ],
                "milestone": None,
                "growth_metrics": [
                    {"type": g.metric_type, "value": g.value, "unit": g.unit}
                    for g in record.growth_metrics
                ],
                "media_files": [],
            }
            if record.milestone:
                rec["milestone"] = {
                    "name": record.milestone.name,
                    "description": record.milestone.description,
                }

            for media in record.media_entries:
                full_path = resolve_media_path(media.original_path)
                if full_path.exists():
                    arc_name = f"media/{record.date}/{full_path.name}"
                    zf.write(full_path, arc_name)
                    rec["media_files"].append(arc_name)

            records_data.append(rec)
            task["progress"] = round((i + 1) / total * 100, 1)

        zf.writestr(
            "records.json",
            json.dumps(records_data, ensure_ascii=False, indent=2),
        )

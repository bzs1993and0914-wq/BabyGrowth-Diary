from fastapi import APIRouter

from app.config import VERSION

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查接口，供 Electron 主进程确认后端是否已就绪。"""
    return {"status": "ok", "version": VERSION}

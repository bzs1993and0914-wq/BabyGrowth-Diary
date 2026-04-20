import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import VERSION
from app.database.init_db import init_db
from app.services.storage_manager import ensure_dirs
from app.api import auth, health, records, media, milestones, export, settings, growth_metrics, parent_words

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI 生命周期管理：启动时初始化存储目录和数据库，关闭时记录日志。"""
    logger.info("Starting BabyGrow backend v%s", VERSION)
    ensure_dirs()
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down BabyGrow backend")


app = FastAPI(
    title="BabyGrow API",
    version=VERSION,
    lifespan=lifespan,
    redirect_slashes=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # JWT 在 Authorization 头；与 allow_origins=["*"] 同时使用时浏览器规范要求 credentials=False
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(records.router, prefix="/api")
app.include_router(media.router, prefix="/api")
app.include_router(milestones.router, prefix="/api")
app.include_router(export.router, prefix="/api")
app.include_router(settings.router, prefix="/api")
app.include_router(growth_metrics.router, prefix="/api")
app.include_router(parent_words.router, prefix="/api")

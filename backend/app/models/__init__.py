from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.models.user import User
from app.models.daily_record import DailyRecord
from app.models.media_entry import MediaEntry
from app.models.text_entry import TextEntry
from app.models.milestone import Milestone
from app.models.milestone_category import MilestoneCategory
from app.models.app_settings import AppSettings
from app.models.growth_metric import GrowthMetric
from app.models.parent_word import ParentWord
from app.models.parent_word_highlight import ParentWordHighlight

__all__ = [
    "Base",
    "User",
    "DailyRecord",
    "MediaEntry",
    "TextEntry",
    "Milestone",
    "MilestoneCategory",
    "AppSettings",
    "GrowthMetric",
    "ParentWord",
    "ParentWordHighlight",
]

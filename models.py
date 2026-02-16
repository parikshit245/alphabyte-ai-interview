"""
Pydantic Models for FastAPI
============================

Aligned with schema.cypher — strict hierarchy:
    QuestionList → Domain → Skill → Topic → Difficulty → Question → Answer
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ─────────────────────────────────────────────
# Response Models (used by recruiter_routes.py)
# ─────────────────────────────────────────────

class SkillResponse(BaseModel):
    skill_id: str
    name: str
    description: Optional[str] = None
    topic_count: int = 0


class TopicResponse(BaseModel):
    topic_id: str
    name: str
    description: Optional[str] = None
    difficulty_count: int = 0


class DifficultyResponse(BaseModel):
    difficulty_id: str
    level: str
    question_count: int = 0


class AnswerResponse(BaseModel):
    answer_id: str
    explanation: Optional[str] = None
    code: Optional[str] = None
    code_explanation: Optional[str] = None


class QuestionResponse(BaseModel):
    question_id: str
    title: str
    description: Optional[str] = None
    hints: Optional[str] = None
    example: Optional[str] = None
    company_ids: List[str] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ─────────────────────────────────────────────
# CSV Bulk-Load (used by company_upload.py)
# ─────────────────────────────────────────────

class CSVLoadNodeResult(BaseModel):
    """Result for a single CSV file / node type"""
    node_type: str
    total_rows: int
    loaded: int
    skipped: int
    errors: List[str] = []

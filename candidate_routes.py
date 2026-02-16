"""
Candidate API Routes
=====================
Endpoints for candidates taking an interview:
  1. POST /candidate/start               — Start a session, get questions (no answers)
  2. POST /candidate/{id}/answer         — Store candidate's response for a question
  3. POST /candidate/{id}/submit         — Submit / finish, receive correct answers back
  4. POST /candidate/{id}/verify_result  — Review: org_answer vs candidate_answer side-by-side
  5. GET  /candidate/{id}/status         — Check session status
  6. GET  /candidate/{id}/answers        — Get all saved candidate answers
"""

from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from dependencies import get_mongo

router = APIRouter(prefix="/candidate", tags=["Candidate"])


# ── Collections ──────────────────────────────────────────────────────

def _sessions():
    """MongoDB collection for candidate sessions."""
    return get_mongo()["candidate_sessions"]


def _interviews():
    """MongoDB collection where recruiter stored interview questions."""
    return get_mongo()["interviews"]


def _candidate_answers():
    """MongoDB collection for candidate answer submissions."""
    return get_mongo()["candidate_answers"]


# ── Request / Response models ────────────────────────────────────────

class StartRequest(BaseModel):
    candidate_id: str = Field(..., min_length=1, description="Unique candidate identifier")
    interview_id: str = Field(..., min_length=1, description="Interview created by recruiter")


class StartResponse(BaseModel):
    session_id: str
    candidate_id: str
    interview_id: str
    total_questions: int
    questions: list
    message: str


class SubmitResponse(BaseModel):
    session_id: str
    candidate_id: str
    interview_id: str
    status: str
    submitted_at: str
    total_questions: int
    questions_with_answers: list
    message: str


class CandidateAnswerRequest(BaseModel):
    question_id: str = Field(..., min_length=1, description="ID of the question being answered")
    answer_text: str = Field(..., min_length=1, description="Candidate's written answer / response")
    code: Optional[str] = Field(None, description="Code snippet if applicable")


class CandidateAnswerResponse(BaseModel):
    session_id: str
    question_id: str
    answer_text: str
    code: Optional[str] = None
    saved_at: str
    message: str


class CandidateAnswersListResponse(BaseModel):
    session_id: str
    total_answered: int
    answers: list


class VerifyQuestionItem(BaseModel):
    question_id: str
    title: str
    difficulty_level: Optional[str] = None
    org_answer: Optional[dict] = None
    candidate_answer: Optional[dict] = None


class VerifyResultResponse(BaseModel):
    session_id: str
    candidate_id: str
    interview_id: str
    total_questions: int
    total_answered: int
    results: List[VerifyQuestionItem]
    message: str


class SessionStatusResponse(BaseModel):
    session_id: str
    candidate_id: str
    interview_id: str
    status: str
    started_at: str
    submitted_at: Optional[str] = None
    total_answered: int = 0


# =====================================================================
#  POST /candidate/start — Begin interview session
# =====================================================================
@router.post(
    "/start",
    response_model=StartResponse,
    summary="Start a candidate interview session",
)
async def start_interview(req: StartRequest):
    """
    Creates a candidate session tied to an existing interview.

    - Looks up the interview in MongoDB (created by recruiter via upload-questions).
    - Returns questions **without answers**.
    - Stores the session so we know when the candidate started.

    The `session_id` is `{candidate_id}_{interview_id}`.
    """
    # ── Fetch interview from MongoDB ──
    interview = _interviews().find_one({"_id": req.interview_id})
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview '{req.interview_id}' not found. "
                   f"Recruiter must create it first via POST /interviews/{{id}}/upload-questions.",
        )

    session_id = f"{req.candidate_id}_{req.interview_id}"

    # ── Check if session already exists ──
    existing = _sessions().find_one({"_id": session_id})
    if existing and existing.get("status") == "submitted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Candidate '{req.candidate_id}' already submitted this interview.",
        )

    # ── Questions without answers (candidate view) ──
    questions = interview.get("questions", [])

    # ── Create / update session doc ──
    session_doc = {
        "_id": session_id,
        "session_id": session_id,
        "candidate_id": req.candidate_id,
        "interview_id": req.interview_id,
        "status": "in_progress",
        "started_at": datetime.utcnow(),
        "submitted_at": None,
        "total_questions": len(questions),
        "total_answered": 0,
    }
    _sessions().replace_one({"_id": session_id}, session_doc, upsert=True)

    return StartResponse(
        session_id=session_id,
        candidate_id=req.candidate_id,
        interview_id=req.interview_id,
        total_questions=len(questions),
        questions=questions,
        message=f"Interview started. {len(questions)} questions loaded.",
    )


# =====================================================================
#  POST /candidate/{session_id}/answer — Store candidate response
# =====================================================================
@router.post(
    "/{session_id}/answer",
    response_model=CandidateAnswerResponse,
    summary="Save candidate's answer for a question",
)
async def save_candidate_answer(session_id: str, req: CandidateAnswerRequest):
    """
    Stores the candidate's response for a single question.

    - Can be called multiple times per question (overwrites previous answer).
    - Session must be `in_progress` (not yet submitted).
    - Answers are stored in the `candidate_answers` collection,
      keyed by `{session_id}_{question_id}`.
    """
    # ── Validate session ──
    session = _sessions().find_one({"_id": session_id})
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found. Call POST /candidate/start first.",
        )
    if session.get("status") == "submitted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot save answers — interview already submitted.",
        )

    # ── Validate question belongs to this interview ──
    interview = _interviews().find_one({"_id": session["interview_id"]})
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview '{session['interview_id']}' no longer exists.",
        )
    valid_qids = {q["question_id"] for q in interview.get("questions", [])}
    if req.question_id not in valid_qids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Question '{req.question_id}' is not part of this interview.",
        )

    # ── Store / overwrite candidate answer ──
    now = datetime.utcnow()
    answer_id = f"{session_id}_{req.question_id}"
    answer_doc = {
        "_id": answer_id,
        "session_id": session_id,
        "candidate_id": session["candidate_id"],
        "interview_id": session["interview_id"],
        "question_id": req.question_id,
        "answer_text": req.answer_text,
        "code": req.code,
        "saved_at": now,
    }
    _candidate_answers().replace_one({"_id": answer_id}, answer_doc, upsert=True)

    # ── Update answered count on session ──
    total_answered = _candidate_answers().count_documents({"session_id": session_id})
    _sessions().update_one(
        {"_id": session_id},
        {"$set": {"total_answered": total_answered}},
    )

    return CandidateAnswerResponse(
        session_id=session_id,
        question_id=req.question_id,
        answer_text=req.answer_text,
        code=req.code,
        saved_at=now.isoformat(),
        message=f"Answer saved for question '{req.question_id}'. "
                f"{total_answered}/{session['total_questions']} answered.",
    )


# =====================================================================
#  POST /candidate/{session_id}/submit — Finish & get answers
# =====================================================================
@router.post(
    "/{session_id}/submit",
    response_model=SubmitResponse,
    summary="Submit interview — returns all answers",
)
async def submit_interview(session_id: str):
    """
    Marks the candidate session as **submitted** and returns
    the full question + answer set so the candidate can review.

    - Answers come from the `questions_with_answers` field that the
      recruiter's upload-questions endpoint stored in MongoDB.
    """
    # ── Validate session ──
    session = _sessions().find_one({"_id": session_id})
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found. Call POST /candidate/start first.",
        )

    if session.get("status") == "submitted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This interview has already been submitted.",
        )

    # ── Fetch answers from interview doc ──
    interview = _interviews().find_one({"_id": session["interview_id"]})
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview '{session['interview_id']}' no longer exists.",
        )

    questions_with_answers = interview.get("questions_with_answers", [])

    # ── Gather candidate's saved answers ──
    candidate_answers = list(
        _candidate_answers().find(
            {"session_id": session_id},
            {"_id": 0, "question_id": 1, "answer_text": 1, "code": 1, "saved_at": 1},
        )
    )
    # Convert datetime to string for JSON
    for ca in candidate_answers:
        if hasattr(ca.get("saved_at"), "isoformat"):
            ca["saved_at"] = ca["saved_at"].isoformat()

    # ── Attach candidate answer alongside each correct answer ──
    ca_map = {ca["question_id"]: ca for ca in candidate_answers}
    for q in questions_with_answers:
        q["candidate_answer"] = ca_map.get(q["question_id"])

    # ── Mark session as submitted ──
    now = datetime.utcnow()
    _sessions().update_one(
        {"_id": session_id},
        {"$set": {"status": "submitted", "submitted_at": now}},
    )

    return SubmitResponse(
        session_id=session_id,
        candidate_id=session["candidate_id"],
        interview_id=session["interview_id"],
        status="submitted",
        submitted_at=now.isoformat(),
        total_questions=len(questions_with_answers),
        questions_with_answers=questions_with_answers,
        message="Interview submitted. Here are the answers for review.",
    )


# =====================================================================
#  POST /candidate/{session_id}/verify_result — Review comparison
# =====================================================================
@router.post(
    "/{session_id}/verify_result",
    response_model=VerifyResultResponse,
    summary="Review: org answers vs candidate answers side-by-side",
)
async def verify_result(session_id: str):
    """
    Candidate requests a review after submitting.

    Returns every question with:
      - `org_answer`       — the correct / reference answer from the question bank
      - `candidate_answer` — what the candidate wrote

    Both are placed side-by-side so the candidate (or recruiter)
    can compare and verify the result.

    The session must be in `submitted` status.
    """
    # ── Validate session ──
    session = _sessions().find_one({"_id": session_id})
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )
    if session.get("status") != "submitted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interview not yet submitted. Call POST /candidate/{id}/submit first.",
        )

    # ── Fetch interview (has org answers) ──
    interview = _interviews().find_one({"_id": session["interview_id"]})
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview '{session['interview_id']}' no longer exists.",
        )

    # ── Fetch candidate answers ──
    ca_docs = list(
        _candidate_answers().find(
            {"session_id": session_id},
            {"_id": 0, "question_id": 1, "answer_text": 1, "code": 1, "saved_at": 1},
        )
    )
    for ca in ca_docs:
        if hasattr(ca.get("saved_at"), "isoformat"):
            ca["saved_at"] = ca["saved_at"].isoformat()
    ca_map = {ca["question_id"]: ca for ca in ca_docs}

    # ── Build side-by-side comparison ──
    results = []
    for q in interview.get("questions_with_answers", []):
        # org_answer = first answer from the question bank (explanation + code)
        org_answers = q.get("answers", [])
        org_answer = org_answers[0] if org_answers else None

        results.append(
            VerifyQuestionItem(
                question_id=q["question_id"],
                title=q.get("title", ""),
                difficulty_level=q.get("difficulty_level"),
                org_answer=org_answer,
                candidate_answer=ca_map.get(q["question_id"]),
            )
        )

    return VerifyResultResponse(
        session_id=session_id,
        candidate_id=session["candidate_id"],
        interview_id=session["interview_id"],
        total_questions=len(results),
        total_answered=len(ca_docs),
        results=results,
        message=f"Verification ready: {len(ca_docs)}/{len(results)} questions answered.",
    )


# =====================================================================
#  GET /candidate/{session_id}/status — Check session state
# =====================================================================
@router.get(
    "/{session_id}/status",
    response_model=SessionStatusResponse,
    summary="Check candidate session status",
)
async def get_session_status(session_id: str):
    """Returns whether the session is in_progress or submitted."""
    session = _sessions().find_one({"_id": session_id})
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    return SessionStatusResponse(
        session_id=session["session_id"],
        candidate_id=session["candidate_id"],
        interview_id=session["interview_id"],
        status=session["status"],
        started_at=session["started_at"].isoformat()
            if hasattr(session["started_at"], "isoformat")
            else str(session["started_at"]),
        submitted_at=session["submitted_at"].isoformat()
            if session.get("submitted_at") and hasattr(session["submitted_at"], "isoformat")
            else None,
        total_answered=session.get("total_answered", 0),
    )


# =====================================================================
#  GET /candidate/{session_id}/answers — List all saved answers
# =====================================================================
@router.get(
    "/{session_id}/answers",
    response_model=CandidateAnswersListResponse,
    summary="Get all candidate answers for a session",
)
async def get_candidate_answers(session_id: str):
    """Returns every answer the candidate has saved so far."""
    session = _sessions().find_one({"_id": session_id})
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    answers = list(
        _candidate_answers().find(
            {"session_id": session_id},
            {"_id": 0},
        )
    )
    for a in answers:
        if hasattr(a.get("saved_at"), "isoformat"):
            a["saved_at"] = a["saved_at"].isoformat()

    return CandidateAnswersListResponse(
        session_id=session_id,
        total_answered=len(answers),
        answers=answers,
    )

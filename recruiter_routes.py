"""
Recruiter / Interview API Routes
==================================
All endpoints for the recruiter interview flow:
  - Question graph traversal (Domain → Skill → Topic → Difficulty → Question → Answer)
  - Creating & managing interviews
  - Uploading questions (3:4:3 ratio)
  - Candidate view / Recruiter view
  - Skill selection for interviews
  - Company → interview lookups
  - MongoDB full-document retrieval
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import csv
import io
import uuid

from models import (
    SkillResponse,
    TopicResponse,
    DifficultyResponse,
    QuestionResponse,
    AnswerResponse,
)
from dependencies import (
    get_db,
    get_interviews_collection,
    _interview_cache,
    to_native_dt,
)


# ── Request body for domain selection ────────────────────────────────
class DomainSelectRequest(BaseModel):
    domain_id: str
    job_description: str

router = APIRouter(tags=["Recruiter / Interviews"])


# =====================================================================
#  QUESTION GRAPH TRAVERSAL ENDPOINTS
# =====================================================================

# ── GET topics from a skill ──────────────────────────────────────────
@router.get(
    "/skills/{skill_id}/topics",
    response_model=List[TopicResponse],
    summary="Fetch all Topics under a Skill",
)
async def get_topics_by_skill(skill_id: str, db=Depends(get_db)):
    """
    Traverse  Skill -[:HAS_TOPIC]-> Topic
    and return every Topic node linked to the given skill_id.
    """
    with db.session() as s:
        result = s.run(
            """
            MATCH (sk:Skill {skill_id: $sid})-[:HAS_TOPIC]->(t:Topic)
            OPTIONAL MATCH (t)-[:HAS_DIFFICULTY]->(df:Difficulty)
            RETURN t, count(df) AS difficulty_count
            ORDER BY t.name
            """,
            {"sid": skill_id},
        )
        records = list(result)

    if not records:
        with db.session() as s:
            exists = s.run(
                "MATCH (sk:Skill {skill_id: $sid}) RETURN sk LIMIT 1",
                {"sid": skill_id},
            ).single()
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Skill '{skill_id}' not found",
            )
        return []

    return [
        TopicResponse(
            topic_id=r["t"]["topic_id"],
            name=r["t"]["name"],
            description=r["t"].get("description"),
            difficulty_count=r["difficulty_count"],
        )
        for r in records
    ]


# ── GET difficulties from a topic ────────────────────────────────────
@router.get(
    "/topics/{topic_id}/difficulties",
    response_model=List[DifficultyResponse],
    summary="Fetch all Difficulty levels under a Topic",
)
async def get_difficulties_by_topic(topic_id: str, db=Depends(get_db)):
    """
    Traverse  Topic -[:HAS_DIFFICULTY]-> Difficulty
    and return every Difficulty node linked to the given topic_id.
    """
    with db.session() as s:
        result = s.run(
            """
            MATCH (t:Topic {topic_id: $tid})-[:HAS_DIFFICULTY]->(df:Difficulty)
            OPTIONAL MATCH (df)-[:HAS_QUESTION]->(q:Question)
            RETURN df, count(q) AS question_count
            ORDER BY df.level
            """,
            {"tid": topic_id},
        )
        records = list(result)

    if not records:
        with db.session() as s:
            exists = s.run(
                "MATCH (t:Topic {topic_id: $tid}) RETURN t LIMIT 1",
                {"tid": topic_id},
            ).single()
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Topic '{topic_id}' not found",
            )
        return []

    return [
        DifficultyResponse(
            difficulty_id=r["df"]["difficulty_id"],
            level=r["df"]["level"],
            question_count=r["question_count"],
        )
        for r in records
    ]


# ── GET questions from a difficulty ───────────────────────────────────
@router.get(
    "/difficulties/{difficulty_id}/questions",
    response_model=List[QuestionResponse],
    summary="Fetch all Questions under a Difficulty level",
)
async def get_questions_by_difficulty(difficulty_id: str, db=Depends(get_db)):
    """
    Traverse  Difficulty -[:HAS_QUESTION]-> Question
    and return every Question node linked to the given difficulty_id.
    """
    with db.session() as s:
        result = s.run(
            """
            MATCH (df:Difficulty {difficulty_id: $dfid})-[:HAS_QUESTION]->(q:Question)
            OPTIONAL MATCH (q)-[:HAS_ANSWER]->(a:Answer)
            RETURN q, count(a) AS answer_count
            ORDER BY q.title
            """,
            {"dfid": difficulty_id},
        )
        records = list(result)

    if not records:
        with db.session() as s:
            exists = s.run(
                "MATCH (df:Difficulty {difficulty_id: $dfid}) RETURN df LIMIT 1",
                {"dfid": difficulty_id},
            ).single()
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Difficulty '{difficulty_id}' not found",
            )
        return []

    return [
        QuestionResponse(
            question_id=r["q"]["question_id"],
            title=r["q"]["title"],
            description=r["q"].get("description"),
            hints=r["q"].get("hints"),
            example=r["q"].get("example"),
            company_ids=r["q"].get("company_ids", []),
            created_at=to_native_dt(r["q"].get("created_at")),
            updated_at=to_native_dt(r["q"].get("updated_at")),
        )
        for r in records
    ]


# ── GET answers from a question ───────────────────────────────────────
@router.get(
    "/questions/{question_id}/answers",
    response_model=List[AnswerResponse],
    summary="Fetch all Answers for a Question",
)
async def get_answers_by_question(question_id: str, db=Depends(get_db)):
    """
    Traverse  Question -[:HAS_ANSWER]-> Answer
    and return every Answer node linked to the given question_id.
    """
    with db.session() as s:
        result = s.run(
            """
            MATCH (q:Question {question_id: $qid})-[:HAS_ANSWER]->(a:Answer)
            RETURN a
            ORDER BY a.answer_id
            """,
            {"qid": question_id},
        )
        records = list(result)

    if not records:
        with db.session() as s:
            exists = s.run(
                "MATCH (q:Question {question_id: $qid}) RETURN q LIMIT 1",
                {"qid": question_id},
            ).single()
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question '{question_id}' not found",
            )
        return []

    return [
        AnswerResponse(
            answer_id=r["a"]["answer_id"],
            explanation=r["a"].get("explanation"),
            code=r["a"].get("code"),
            code_explanation=r["a"].get("code_explanation"),
        )
        for r in records
    ]


# ── GET questions from a topic with 3:4:3 ratio ──────────────────────
@router.get(
    "/topics/{topic_id}/questions",
    response_model=List[QuestionResponse],
    summary="Fetch questions under a Topic distributed as Hard:Medium:Easy = 3:4:3",
)
async def get_questions_by_topic(
    topic_id: str,
    total: int = 10,
    company_id: Optional[str] = None,
    db=Depends(get_db),
):
    """
    Fetches questions from all Difficulty levels under a Topic,
    distributed in a **3:4:3** ratio (Hard : Medium : Easy).

    - `total` — total number of questions to fetch (default 10).
    - `company_id` — if provided, only returns questions whose
      company_ids array contains this value.
    - Ratio applied:  Hard = 3/10,  Medium = 4/10,  Easy = 3/10 of `total`.
    - If a bucket has fewer questions than its quota, remaining slots
      are filled from other difficulties.
    """
    company_filter = "AND $cid IN q.company_ids" if company_id else ""

    ratio = {"Hard": 3, "Medium": 4, "Easy": 3}
    ratio_sum = sum(ratio.values())
    quota = {
        level: max(1, round(total * weight / ratio_sum))
        for level, weight in ratio.items()
    }

    with db.session() as s:
        exists = s.run(
            "MATCH (t:Topic {topic_id: $tid}) RETURN t LIMIT 1",
            {"tid": topic_id},
        ).single()
    if not exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic '{topic_id}' not found",
        )

    collected: List[dict] = []
    remaining = total

    with db.session() as s:
        for level in ["Hard", "Medium", "Easy"]:
            limit = min(quota[level], remaining)
            if limit <= 0:
                continue
            rows = list(s.run(
                f"""
                MATCH (t:Topic {{topic_id: $tid}})
                      -[:HAS_DIFFICULTY]->(df:Difficulty {{level: $level}})
                      -[:HAS_QUESTION]->(q:Question)
                WHERE true {company_filter}
                RETURN q, df.level AS difficulty_level
                ORDER BY q.title
                LIMIT $limit
                """,
                {"tid": topic_id, "level": level, "limit": limit,
                 "cid": company_id},
            ))
            collected.extend(rows)
            remaining -= len(rows)

        if remaining > 0:
            already = {r["q"]["question_id"] for r in collected}
            extras = list(s.run(
                f"""
                MATCH (t:Topic {{topic_id: $tid}})
                      -[:HAS_DIFFICULTY]->(df:Difficulty)
                      -[:HAS_QUESTION]->(q:Question)
                WHERE NOT q.question_id IN $skip {company_filter}
                RETURN q, df.level AS difficulty_level
                ORDER BY q.title
                LIMIT $limit
                """,
                {"tid": topic_id, "skip": list(already), "limit": remaining,
                 "cid": company_id},
            ))
            collected.extend(extras)

    return [
        QuestionResponse(
            question_id=r["q"]["question_id"],
            title=r["q"]["title"],
            description=r["q"].get("description"),
            hints=r["q"].get("hints"),
            example=r["q"].get("example"),
            company_ids=r["q"].get("company_ids", []),
            created_at=to_native_dt(r["q"].get("created_at")),
            updated_at=to_native_dt(r["q"].get("updated_at")),
        )
        for r in collected
    ]


# ── GET all skills with full hierarchy details ────────────────────────
@router.get(
    "/skills",
    summary="List all Skills with domain, topics, difficulties, and question counts",
)
async def get_all_skills(db=Depends(get_db)):
    """
    Returns every Skill in the DB along with:
      - parent Domain name & id
      - list of Topics under the Skill
      - total question count per difficulty level
      - overall question count

    This is the master list the system uses to know
    which skills have data available for interview preparation.
    """
    with db.session() as s:
        rows = list(s.run("""
            MATCH (d:Domain)-[:HAS_SKILL]->(sk:Skill)
            OPTIONAL MATCH (sk)-[:HAS_TOPIC]->(t:Topic)
            OPTIONAL MATCH (t)-[:HAS_DIFFICULTY]->(df:Difficulty)
            OPTIONAL MATCH (df)-[:HAS_QUESTION]->(q:Question)
            WITH d, sk,
                 collect(DISTINCT {
                     topic_id: t.topic_id,
                     topic_name: t.name
                 }) AS topics,
                 count(DISTINCT t) AS topic_count,
                 count(DISTINCT q) AS total_questions,
                 sum(CASE WHEN df.level = 'Easy'   THEN 1 ELSE 0 END) AS easy,
                 sum(CASE WHEN df.level = 'Medium' THEN 1 ELSE 0 END) AS medium,
                 sum(CASE WHEN df.level = 'Hard'   THEN 1 ELSE 0 END) AS hard
            RETURN sk.skill_id   AS skill_id,
                   sk.name       AS skill_name,
                   sk.description AS skill_description,
                   d.domain_id   AS domain_id,
                   d.name        AS domain_name,
                   topic_count,
                   topics,
                   total_questions,
                   easy, medium, hard
            ORDER BY d.name, sk.name
        """))

    result = []
    for r in rows:
        topics = [t for t in r["topics"]
                  if t.get("topic_id") is not None]
        result.append({
            "skill_id":          r["skill_id"],
            "skill_name":        r["skill_name"],
            "skill_description": r["skill_description"],
            "domain_id":         r["domain_id"],
            "domain_name":       r["domain_name"],
            "topic_count":       r["topic_count"],
            "topics":            topics,
            "total_questions":   r["total_questions"],
            "questions_by_difficulty": {
                "easy":   r["easy"],
                "medium": r["medium"],
                "hard":   r["hard"],
            },
        })

    return result


# =====================================================================
#  INTERVIEW MANAGEMENT ENDPOINTS
# =====================================================================

# ── POST — Select a domain for an interview + job description ────────
@router.post(
    "/interviews/{interview_id}/domain",
    summary="Select a domain and provide job description for an interview",
)
async def select_interview_domain(
    interview_id: str,
    body: DomainSelectRequest,
    db=Depends(get_db),
):
    """
    Recruiter selects a domain and supplies a job description.
    Both are saved to the in-memory interview cache.
    Returns the domain info along with its skills so the recruiter
    can proceed to skill selection.
    """
    domain_id = body.domain_id
    job_description = body.job_description

    # ── Validate domain & fetch its skills ──
    with db.session() as s:
        domain_row = s.run(
            "MATCH (d:Domain {domain_id: $did}) RETURN d LIMIT 1",
            {"did": domain_id},
        ).single()

    if not domain_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Domain '{domain_id}' not found",
        )

    with db.session() as s:
        skill_rows = list(s.run(
            """
            MATCH (d:Domain {domain_id: $did})-[:HAS_SKILL]->(sk:Skill)
            OPTIONAL MATCH (sk)-[:HAS_TOPIC]->(t:Topic)
            RETURN sk, count(t) AS topic_count
            ORDER BY sk.name
            """,
            {"did": domain_id},
        ))

    skills = [
        {
            "skill_id": r["sk"]["skill_id"],
            "name": r["sk"]["name"],
            "description": r["sk"].get("description"),
            "topic_count": r["topic_count"],
        }
        for r in skill_rows
    ]

    # ── Save to cache ──
    _interview_cache.setdefault(interview_id, {})
    _interview_cache[interview_id].update({
        "interview_id": interview_id,
        "domain_id": domain_id,
        "domain_name": domain_row["d"].get("name"),
        "job_description": job_description,
        "created_at": datetime.utcnow().isoformat(),
    })

    return {
        "interview_id": interview_id,
        "domain_id": domain_id,
        "domain_name": domain_row["d"].get("name"),
        "job_description": job_description,
        "skills": skills,
    }


# ── POST — Fetch questions (3:4:3) and cache them for an interview ───
@router.post(
    "/interviews/{interview_id}/upload-questions",
    summary="Fetch questions (3:4:3) and cache them for an interview",
)
async def upload_interview_questions(
    interview_id: str,
    topic_id: str,
    total: int = 10,
    company_id: Optional[str] = None,
    db=Depends(get_db),
):
    """
    Fetches questions from Neo4j using the 3:4:3 ratio logic,
    then stores the result in an in-memory cache keyed by `interview_id`.

    - If `company_id` is provided, only questions matching that company are included.
    - Subsequent calls with the same `interview_id` will **overwrite** the cache.
    """
    company_filter = "AND $cid IN q.company_ids" if company_id else ""

    ratio = {"Hard": 3, "Medium": 4, "Easy": 3}
    ratio_sum = sum(ratio.values())
    quota = {
        level: max(1, round(total * weight / ratio_sum))
        for level, weight in ratio.items()
    }

    # ── Validate topic ──
    with db.session() as s:
        exists = s.run(
            "MATCH (t:Topic {topic_id: $tid}) RETURN t LIMIT 1",
            {"tid": topic_id},
        ).single()
    if not exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic '{topic_id}' not found",
        )

    # ── Fetch with 3:4:3 ──
    collected: List[dict] = []
    remaining = total

    with db.session() as s:
        for level in ["Hard", "Medium", "Easy"]:
            limit = min(quota[level], remaining)
            if limit <= 0:
                continue
            rows = list(s.run(
                f"""
                MATCH (t:Topic {{topic_id: $tid}})
                      -[:HAS_DIFFICULTY]->(df:Difficulty {{level: $level}})
                      -[:HAS_QUESTION]->(q:Question)
                WHERE true {company_filter}
                RETURN q, df.level AS difficulty_level
                ORDER BY q.title
                LIMIT $limit
                """,
                {"tid": topic_id, "level": level, "limit": limit,
                 "cid": company_id},
            ))
            collected.extend(rows)
            remaining -= len(rows)

        if remaining > 0:
            already = {r["q"]["question_id"] for r in collected}
            extras = list(s.run(
                f"""
                MATCH (t:Topic {{topic_id: $tid}})
                      -[:HAS_DIFFICULTY]->(df:Difficulty)
                      -[:HAS_QUESTION]->(q:Question)
                WHERE NOT q.question_id IN $skip {company_filter}
                RETURN q, df.level AS difficulty_level
                ORDER BY q.title
                LIMIT $limit
                """,
                {"tid": topic_id, "skip": list(already), "limit": remaining,
                 "cid": company_id},
            ))
            collected.extend(extras)

    # ── Build question list (without answers — candidate view) ──
    question_ids = [r["q"]["question_id"] for r in collected]
    questions = []
    questions_with_answers = []  # recruiter view (includes answers)

    # Fetch answers for all collected questions in one query
    answers_map: Dict[str, list] = {}
    if question_ids:
        with db.session() as s:
            ans_rows = list(s.run("""
                MATCH (q:Question)-[:HAS_ANSWER]->(a:Answer)
                WHERE q.question_id IN $qids
                RETURN q.question_id AS qid,
                       a.answer_id AS answer_id,
                       a.explanation AS explanation,
                       a.code AS code,
                       a.code_explanation AS code_explanation
            """, {"qids": question_ids}))
            for ar in ans_rows:
                answers_map.setdefault(ar["qid"], []).append({
                    "answer_id": ar["answer_id"],
                    "explanation": ar["explanation"],
                    "code": ar["code"],
                    "code_explanation": ar["code_explanation"],
                })

    for r in collected:
        q_data = {
            "question_id": r["q"]["question_id"],
            "title": r["q"]["title"],
            "description": r["q"].get("description"),
            "hints": r["q"].get("hints"),
            "example": r["q"].get("example"),
            "company_ids": r["q"].get("company_ids", []),
            "difficulty_level": r["difficulty_level"],
            "created_at": str(r["q"].get("created_at")) if r["q"].get("created_at") else None,
            "updated_at": str(r["q"].get("updated_at")) if r["q"].get("updated_at") else None,
        }
        questions.append(q_data)
        questions_with_answers.append({
            **q_data,
            "answers": answers_map.get(r["q"]["question_id"], []),
        })

    # ── Store in cache ──
    _interview_cache.setdefault(interview_id, {})
    _interview_cache[interview_id].update({
        "interview_id": interview_id,
        "topic_id": topic_id,
        "company_id": company_id,
        "total_requested": total,
        "total_cached": len(questions),
        "created_at": datetime.utcnow().isoformat(),
        "questions": questions,                          # candidate view
        "questions_with_answers": questions_with_answers,  # recruiter view
    })

    # ── Persist to MongoDB ──
    mongo_doc = {
        "_id": interview_id,
        "interview_id": interview_id,
        "topic_id": topic_id,
        "company_id": company_id,
        "total_requested": total,
        "total_questions": len(questions),
        "created_at": datetime.utcnow(),
        "questions": questions,
        "questions_with_answers": questions_with_answers,
        "skills": _interview_cache[interview_id].get("skills", []),
        "skill_ids": _interview_cache[interview_id].get("skill_ids", []),
        "domain_id": _interview_cache[interview_id].get("domain_id"),
        "domain_name": _interview_cache[interview_id].get("domain_name"),
        "job_description": _interview_cache[interview_id].get("job_description"),
    }
    col = get_interviews_collection()
    col.replace_one({"_id": interview_id}, mongo_doc, upsert=True)

    # ── Create Interview node in Neo4j company graph ──
    with db.session() as s:
        s.run("""
            MERGE (iv:Interview {interview_id: $iid})
            ON CREATE SET
                iv.topic_id       = $tid,
                iv.company_id     = $cid,
                iv.total_questions = $total_q,
                iv.created_at     = datetime()
            ON MATCH SET
                iv.topic_id       = $tid,
                iv.company_id     = $cid,
                iv.total_questions = $total_q,
                iv.updated_at     = datetime()
        """, {
            "iid": interview_id,
            "tid": topic_id,
            "cid": company_id,
            "total_q": len(questions),
        })
        # Link Interview to Company if company_id is provided
        if company_id:
            s.run("""
                MATCH (c:Company {company_id: $cid})
                MATCH (iv:Interview {interview_id: $iid})
                MERGE (c)-[:HAS_INTERVIEW]->(iv)
            """, {"cid": company_id, "iid": interview_id})

    return {
        "status": "cached_and_persisted",
        "interview_id": interview_id,
        "total_cached": len(questions),
        "message": f"{len(questions)} questions cached for interview {interview_id}",
        "persisted_to": ["mongodb", "neo4j_company_graph"],
    }


# =====================================================================
#  GET — Candidate view (questions only, no answers)
# =====================================================================
@router.get(
    "/interviews/{interview_id}/questions",
    response_model=List[QuestionResponse],
    summary="Get cached questions for an interview",
)
async def get_interview_questions(interview_id: str):
    """
    Returns the previously cached questions for the given interview_id.
    No DB call — served directly from in-memory cache.
    """
    if interview_id not in _interview_cache:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No questions cached for interview '{interview_id}'. "
                   f"Call POST /interviews/{interview_id}/upload-questions first.",
        )
    return _interview_cache[interview_id]["questions"]


# =====================================================================
#  GET — Recruiter view (questions + answers + difficulty)
# =====================================================================
@router.get(
    "/interviews/{interview_id}/recruiter",
    summary="Recruiter view — all questions with answers for an interview",
)
async def get_interview_recruiter_view(interview_id: str):
    """
    Returns the full question + answer set for the recruiter.
    Includes difficulty_level and all answers per question.
    Served from cache — no DB call.
    """
    if interview_id not in _interview_cache:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No data cached for interview '{interview_id}'",
        )
    cache = _interview_cache[interview_id]
    return {
        "interview_id": interview_id,
        "topic_id": cache.get("topic_id"),
        "company_id": cache.get("company_id"),
        "total_questions": cache.get("total_cached", 0),
        "skills": cache.get("skills", []),
        "questions": cache.get("questions_with_answers", []),
        "created_at": cache.get("created_at"),
    }


# =====================================================================
#  GET — List all cached interviews
# =====================================================================
@router.get(
    "/interviews",
    summary="List all cached interview IDs",
)
async def list_interviews():
    """Returns metadata for every cached interview (without the full question list)."""
    return [
        {
            "interview_id": iid,
            "topic_id": data.get("topic_id"),
            "company_id": data.get("company_id"),
            "total_cached": data.get("total_cached", 0),
            "created_at": data.get("created_at"),
            "has_skills": bool(data.get("skills")),
            "has_questions": bool(data.get("questions")),
        }
        for iid, data in _interview_cache.items()
    ]


# =====================================================================
#  DELETE — Remove cached interview
# =====================================================================
@router.delete(
    "/interviews/{interview_id}",
    summary="Remove cached questions for an interview",
)
async def delete_interview_cache(interview_id: str):
    if interview_id not in _interview_cache:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No cache found for interview '{interview_id}'",
        )
    del _interview_cache[interview_id]
    return {"status": "deleted", "interview_id": interview_id}


# =====================================================================
#  POST — Register selected skills for an interview
# =====================================================================
@router.post(
    "/interviews/{interview_id}/skills",
    summary="Receive selected skill IDs and return their full details",
)
async def receive_interview_skills(
    interview_id: str,
    skill_ids: List[str],
    db=Depends(get_db),
):
    """
    Frontend sends the list of skill_ids the user selected.
    Server fetches full details (topics, question counts, difficulty breakdown)
    for each skill and stores the selection in the interview cache.

    Request body: `["S_JS", "S_REACT", "S_ARRAY"]`
    """
    if not skill_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="skill_ids list cannot be empty",
        )

    with db.session() as s:
        rows = list(s.run("""
            MATCH (d:Domain)-[:HAS_SKILL]->(sk:Skill)
            WHERE sk.skill_id IN $sids
            OPTIONAL MATCH (sk)-[:HAS_TOPIC]->(t:Topic)
            OPTIONAL MATCH (t)-[:HAS_DIFFICULTY]->(df:Difficulty)
            OPTIONAL MATCH (df)-[:HAS_QUESTION]->(q:Question)
            WITH d, sk,
                 collect(DISTINCT {
                     topic_id: t.topic_id,
                     topic_name: t.name
                 }) AS topics,
                 count(DISTINCT t) AS topic_count,
                 count(DISTINCT q) AS total_questions,
                 sum(CASE WHEN df.level = 'Easy'   THEN 1 ELSE 0 END) AS easy,
                 sum(CASE WHEN df.level = 'Medium' THEN 1 ELSE 0 END) AS medium,
                 sum(CASE WHEN df.level = 'Hard'   THEN 1 ELSE 0 END) AS hard
            RETURN sk.skill_id    AS skill_id,
                   sk.name        AS skill_name,
                   sk.description AS skill_description,
                   d.domain_id    AS domain_id,
                   d.name         AS domain_name,
                   topic_count,
                   topics,
                   total_questions,
                   easy, medium, hard
            ORDER BY d.name, sk.name
        """, {"sids": skill_ids}))

    # Build response & detect missing IDs
    found_ids = set()
    skills_detail = []
    for r in rows:
        found_ids.add(r["skill_id"])
        topics = [t for t in r["topics"] if t.get("topic_id") is not None]
        skills_detail.append({
            "skill_id":          r["skill_id"],
            "skill_name":        r["skill_name"],
            "skill_description": r["skill_description"],
            "domain_id":         r["domain_id"],
            "domain_name":       r["domain_name"],
            "topic_count":       r["topic_count"],
            "topics":            topics,
            "total_questions":   r["total_questions"],
            "questions_by_difficulty": {
                "easy":   r["easy"],
                "medium": r["medium"],
                "hard":   r["hard"],
            },
        })

    not_found = [sid for sid in skill_ids if sid not in found_ids]

    # Store selection in interview cache
    _interview_cache.setdefault(interview_id, {})
    _interview_cache[interview_id]["skills"] = skills_detail
    _interview_cache[interview_id]["skill_ids"] = list(found_ids)
    _interview_cache[interview_id]["updated_at"] = datetime.utcnow().isoformat()

    return {
        "interview_id":  interview_id,
        "skills_received": len(found_ids),
        "skills":        skills_detail,
        "not_found":     not_found,
    }


# =====================================================================
#  GET — Company's interviews from Neo4j
# =====================================================================
@router.get(
    "/companies/{company_id}/interviews",
    summary="List all interviews linked to a Company in Neo4j",
)
async def get_company_interviews(company_id: str, db=Depends(get_db)):
    """
    Fetches all Interview nodes linked to the given Company
    via Company -[:HAS_INTERVIEW]-> Interview in the company graph.
    """
    with db.session() as s:
        # Verify company exists
        comp = s.run(
            "MATCH (c:Company {company_id: $cid}) RETURN c LIMIT 1",
            {"cid": company_id},
        ).single()
        if not comp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company '{company_id}' not found",
            )

        rows = list(s.run("""
            MATCH (c:Company {company_id: $cid})-[:HAS_INTERVIEW]->(iv:Interview)
            RETURN iv
            ORDER BY iv.created_at DESC
        """, {"cid": company_id}))

    return {
        "company_id": company_id,
        "company_name": comp["c"].get("name"),
        "total_interviews": len(rows),
        "interviews": [
            {
                "interview_id":    r["iv"]["interview_id"],
                "topic_id":        r["iv"].get("topic_id"),
                "total_questions": r["iv"].get("total_questions"),
                "created_at":      str(r["iv"].get("created_at")) if r["iv"].get("created_at") else None,
                "updated_at":      str(r["iv"].get("updated_at")) if r["iv"].get("updated_at") else None,
            }
            for r in rows
        ],
    }


# =====================================================================
#  GET — Full interview data from MongoDB
# =====================================================================
@router.get(
    "/interviews/{interview_id}/full",
    summary="Get full interview data from MongoDB",
)
async def get_interview_from_mongo(interview_id: str):
    """
    Retrieves the complete interview document (questions + answers)
    from MongoDB. Falls back to in-memory cache if not in Mongo.
    """
    col = get_interviews_collection()
    doc = col.find_one({"_id": interview_id})

    if doc:
        doc["_id"] = str(doc["_id"])  # make JSON-serializable
        return doc

    # Fallback to in-memory cache
    if interview_id in _interview_cache:
        return {
            **_interview_cache[interview_id],
            "source": "in_memory_cache",
        }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Interview '{interview_id}' not found in MongoDB or cache",
    )


# =====================================================================
#  POST — Upload CSV to add questions to Neo4j database
# =====================================================================
@router.post(
    "/upload-questions-csv",
    summary="Upload a CSV file to bulk-add questions to the Neo4j database",
)
async def upload_questions_csv(
    company_id: str = Form(..., description="Company ID to attach to every question"),
    file: UploadFile = File(..., description="CSV file with question data"),
    db=Depends(get_db),
):
    """
    Accepts a CSV file and a company_id.
    Each row creates/merges the full hierarchy in Neo4j:
        QuestionList → Domain → Skill → Topic → Difficulty → Question → Answer

    **Required CSV columns:**
    `question_id`, `title`, `description`, `hints`, `example`,
    `difficulty_level` (Easy/Medium/Hard),
    `topic_id`, `topic_name`,
    `skill_id`, `skill_name`,
    `domain_id`, `domain_name`,
    `answer_id`, `explanation`, `code`, `code_explanation`

    **Optional columns:**
    `list_id`, `list_name`, `list_description`,
    `topic_description`, `skill_description`, `domain_description`,
    `difficulty_id`

    The provided `company_id` is appended to each question's `company_ids` array.
    """
    # ── Validate file type ──
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .csv files are accepted",
        )

    # ── Read & parse CSV ──
    content = await file.read()
    try:
        text = content.decode("utf-8-sig")  # handles BOM
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)

    if not rows:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file is empty or has no data rows",
        )

    # ── Validate required columns ──
    required_cols = {
        "question_id", "title", "description",
        "difficulty_level",
        "topic_id", "topic_name",
        "skill_id", "skill_name",
        "domain_id", "domain_name",
        "answer_id", "explanation",
    }
    header_cols = set(rows[0].keys())
    missing = required_cols - header_cols
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CSV is missing required columns: {sorted(missing)}",
        )

    # ── Insert each row into Neo4j ──
    loaded = 0
    skipped = 0
    errors_list: List[str] = []

    with db.session() as s:
        for idx, row in enumerate(rows, start=2):  # row 2 = first data row
            try:
                # Build IDs / defaults for optional columns
                list_id = row.get("list_id", "").strip() or "QL_DEFAULT"
                list_name = row.get("list_name", "").strip() or "Default Question List"
                list_desc = row.get("list_description", "").strip() or None
                domain_desc = row.get("domain_description", "").strip() or None
                skill_desc = row.get("skill_description", "").strip() or None
                topic_desc = row.get("topic_description", "").strip() or None
                diff_level = row["difficulty_level"].strip()
                diff_id = (
                    row.get("difficulty_id", "").strip()
                    or f"DF_{row['topic_id'].strip()}_{diff_level.upper()}"
                )

                # company_ids: merge with existing
                s.run("""
                    MERGE (ql:QuestionList {list_id: $list_id})
                    ON CREATE SET
                        ql.name        = $list_name,
                        ql.description = $list_desc,
                        ql.created_at  = datetime()

                    MERGE (d:Domain {domain_id: $domain_id})
                    ON CREATE SET
                        d.name        = $domain_name,
                        d.description = $domain_desc

                    MERGE (ql)-[:HAS_DOMAIN]->(d)

                    MERGE (sk:Skill {skill_id: $skill_id})
                    ON CREATE SET
                        sk.name        = $skill_name,
                        sk.description = $skill_desc

                    MERGE (d)-[:HAS_SKILL]->(sk)

                    MERGE (t:Topic {topic_id: $topic_id})
                    ON CREATE SET
                        t.name        = $topic_name,
                        t.description = $topic_desc

                    MERGE (sk)-[:HAS_TOPIC]->(t)

                    MERGE (df:Difficulty {difficulty_id: $diff_id})
                    ON CREATE SET
                        df.level = $diff_level

                    MERGE (t)-[:HAS_DIFFICULTY]->(df)

                    MERGE (q:Question {question_id: $question_id})
                    ON CREATE SET
                        q.title       = $title,
                        q.description = $description,
                        q.hints       = $hints,
                        q.example     = $example,
                        q.company_ids = [$company_id],
                        q.created_at  = datetime()
                    ON MATCH SET
                        q.updated_at  = datetime(),
                        q.company_ids = CASE
                            WHEN NOT $company_id IN coalesce(q.company_ids, [])
                            THEN coalesce(q.company_ids, []) + $company_id
                            ELSE q.company_ids
                        END

                    MERGE (df)-[:HAS_QUESTION]->(q)

                    MERGE (a:Answer {answer_id: $answer_id})
                    ON CREATE SET
                        a.explanation      = $explanation,
                        a.code             = $code,
                        a.code_explanation = $code_explanation,
                        a.company_id       = $company_id
                    ON MATCH SET
                        a.explanation      = $explanation,
                        a.code             = $code,
                        a.code_explanation = $code_explanation,
                        a.company_id       = $company_id

                    MERGE (q)-[:HAS_ANSWER]->(a)
                """, {
                    "list_id":          list_id,
                    "list_name":        list_name,
                    "list_desc":        list_desc,
                    "domain_id":        row["domain_id"].strip(),
                    "domain_name":      row["domain_name"].strip(),
                    "domain_desc":      domain_desc,
                    "skill_id":         row["skill_id"].strip(),
                    "skill_name":       row["skill_name"].strip(),
                    "skill_desc":       skill_desc,
                    "topic_id":         row["topic_id"].strip(),
                    "topic_name":       row["topic_name"].strip(),
                    "topic_desc":       topic_desc,
                    "diff_id":          diff_id,
                    "diff_level":       diff_level,
                    "question_id":      row["question_id"].strip(),
                    "title":            row["title"].strip(),
                    "description":      row.get("description", "").strip() or None,
                    "hints":            row.get("hints", "").strip() or None,
                    "example":          row.get("example", "").strip() or None,
                    "company_id":       company_id,
                    "answer_id":        row["answer_id"].strip(),
                    "explanation":      row.get("explanation", "").strip() or None,
                    "code":             row.get("code", "").strip() or None,
                    "code_explanation": row.get("code_explanation", "").strip() or None,
                })

                loaded += 1

            except Exception as e:
                skipped += 1
                errors_list.append(f"Row {idx}: {str(e)}")

    return {
        "status": "completed",
        "company_id": company_id,
        "file_name": file.filename,
        "total_rows": len(rows),
        "loaded": loaded,
        "skipped": skipped,
        "errors": errors_list,
    }

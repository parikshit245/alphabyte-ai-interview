"""
FastAPI – Technical Questions Knowledge Graph
==============================================

Question Graph hierarchy (schema.cypher):
    QuestionList → Domain → Skill → Topic → Difficulty → Question → Answer

All API endpoints live in recruiter_routes.py
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dependencies import shutdown_connections
from recruiter_routes import router as recruiter_router
from candidate_routes import router as candidate_router

# ── App setup ────────────────────────────────────────────────────────
app = FastAPI(
    title="Technical Questions Knowledge Graph API",
    version="2.0.0",
    description="Neo4j-backed question bank with strict hierarchy",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include all routes ───────────────────────────────────────────────
app.include_router(recruiter_router)
app.include_router(candidate_router)


# ── Shutdown ─────────────────────────────────────────────────────────
@app.on_event("shutdown")
def shutdown():
    shutdown_connections()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

"""
Test: Full Recruiter + Candidate Flow
======================================
Tests every endpoint in the correct workflow order:

  1. Upload CSV (with company_id) → populates Neo4j
  2. Select domain + job description → cache
  3. Graph traversal: skills → topics → difficulties → questions → answers
  4. Register skills for interview
  5. Upload-questions (3:4:3) for interview → cache + MongoDB
  6. Recruiter views (questions, recruiter view, list, full from Mongo)
  7. Candidate flow: start → answer → submit → verify → status → answers list
  8. Cleanup: delete interview cache

Run:  python test_files/test_all.py
"""

import requests
import os
import sys
import json

BASE = "http://localhost:8000"

# ── Tracking ─────────────────────────────────────────────────────────
passed = 0
failed = 0
total  = 0


def test(name: str, response, expected_status=200, check_fn=None):
    """Helper to assert status code and optional body check."""
    global passed, failed, total
    total += 1
    ok = True
    try:
        assert response.status_code == expected_status, \
            f"Expected {expected_status}, got {response.status_code}: {response.text[:300]}"
        if check_fn:
            data = response.json()
            check_fn(data)
        passed += 1
        print(f"  [PASS] {name}")
    except AssertionError as e:
        failed += 1
        print(f"  [FAIL] {name} — {e}")
        ok = False
    return ok


# ── Resolve path to sample CSV ──────────────────────────────────────
CSV_PATH = os.path.join(os.path.dirname(__file__), "sample_questions.csv")
if not os.path.exists(CSV_PATH):
    print(f"ERROR: sample CSV not found at {CSV_PATH}")
    sys.exit(1)


# =====================================================================
print("\n" + "=" * 60)
print("  1. UPLOAD CSV — bulk add questions to Neo4j")
print("=" * 60)

COMPANY_ID = "COMP_TEST_001"

with open(CSV_PATH, "rb") as f:
    r = requests.post(
        f"{BASE}/upload-questions-csv",
        data={"company_id": COMPANY_ID},
        files={"file": ("sample_questions.csv", f, "text/csv")},
    )

test("Upload CSV", r, 200, lambda d: (
    assert_key(d, "loaded"),
    assert_val(d["loaded"] >= 6, f"Expected >=6 loaded, got {d['loaded']}"),
))


def assert_key(d, k):
    assert k in d, f"Missing key '{k}' in response"

def assert_val(cond, msg=""):
    assert cond, msg


# Re-define test with assert helpers inlined (they need to exist before first use)
# Re-run CSV upload since helpers were defined after first call
with open(CSV_PATH, "rb") as f:
    r = requests.post(
        f"{BASE}/upload-questions-csv",
        data={"company_id": COMPANY_ID},
        files={"file": ("sample_questions.csv", f, "text/csv")},
    )

# Reset counters
passed = 0
failed = 0
total  = 0

def check_csv(d):
    assert "loaded" in d, "Missing 'loaded'"
    assert d["loaded"] >= 6, f"Expected >=6, got {d['loaded']}"
    assert d["company_id"] == COMPANY_ID
    print(f"       → Loaded {d['loaded']}/{d['total_rows']} rows, skipped {d['skipped']}")
    if d["errors"]:
        print(f"       → Errors: {d['errors'][:3]}")

test("Upload CSV (6 questions, company_id attached)", r, 200, check_csv)


# =====================================================================
print("\n" + "=" * 60)
print("  2. SELECT DOMAIN + JOB DESCRIPTION")
print("=" * 60)

INTERVIEW_ID = "INT_TEST_001"

r = requests.post(
    f"{BASE}/interviews/{INTERVIEW_ID}/domain",
    json={"domain_id": "D_FRONTEND", "job_description": "Senior Frontend Developer with React and JS expertise"},
)

def check_domain(d):
    assert d["domain_id"] == "D_FRONTEND"
    assert "job_description" in d
    assert len(d.get("skills", [])) > 0, "Expected skills in response"
    print(f"       → Domain: {d['domain_name']}, Skills: {len(d['skills'])}")

test("Select domain + job description", r, 200, check_domain)

# Save skill IDs for later
skills_from_domain = []
if r.status_code == 200:
    skills_from_domain = [s["skill_id"] for s in r.json().get("skills", [])]


# =====================================================================
print("\n" + "=" * 60)
print("  3. GRAPH TRAVERSAL — Skill → Topic → Difficulty → Question → Answer")
print("=" * 60)

# 3a. Skills → Topics
SKILL_ID = "S_JAVASCRIPT"  # from CSV
r = requests.get(f"{BASE}/skills/{SKILL_ID}/topics")

topic_id = None
def check_topics(d):
    global topic_id
    assert len(d) > 0, "Expected at least 1 topic"
    topic_id = d[0]["topic_id"]
    print(f"       → {len(d)} topics found, first: {d[0]['name']}")

test("GET skills/{id}/topics", r, 200, check_topics)

# 3b. Topics → Difficulties
if topic_id:
    r = requests.get(f"{BASE}/topics/{topic_id}/difficulties")
    diff_id = None
    def check_diffs(d):
        global diff_id
        assert len(d) > 0, "Expected at least 1 difficulty"
        diff_id = d[0]["difficulty_id"]
        print(f"       → {len(d)} difficulties, first: {d[0]['level']}")
    test("GET topics/{id}/difficulties", r, 200, check_diffs)
else:
    print("  [SKIP] No topic_id to test difficulties")

# 3c. Difficulties → Questions
if diff_id:
    r = requests.get(f"{BASE}/difficulties/{diff_id}/questions")
    question_id = None
    def check_questions(d):
        global question_id
        assert len(d) > 0, "Expected at least 1 question"
        question_id = d[0]["question_id"]
        assert COMPANY_ID in d[0].get("company_ids", []), \
            f"company_id '{COMPANY_ID}' not in question's company_ids"
        print(f"       → {len(d)} questions, first: {d[0]['title'][:50]}")
    test("GET difficulties/{id}/questions (company_id present)", r, 200, check_questions)
else:
    print("  [SKIP] No diff_id to test questions")

# 3d. Questions → Answers
if question_id:
    r = requests.get(f"{BASE}/questions/{question_id}/answers")
    def check_answers(d):
        assert len(d) > 0, "Expected at least 1 answer"
        print(f"       → {len(d)} answers, explanation: {(d[0].get('explanation') or '')[:60]}...")
    test("GET questions/{id}/answers", r, 200, check_answers)
else:
    print("  [SKIP] No question_id to test answers")


# =====================================================================
print("\n" + "=" * 60)
print("  4. GET ALL SKILLS (master list)")
print("=" * 60)

r = requests.get(f"{BASE}/skills")
def check_all_skills(d):
    assert len(d) > 0, "Expected skills"
    print(f"       → {len(d)} skills total")
test("GET /skills", r, 200, check_all_skills)


# =====================================================================
print("\n" + "=" * 60)
print("  5. REGISTER SKILLS FOR INTERVIEW")
print("=" * 60)

if skills_from_domain:
    r = requests.post(
        f"{BASE}/interviews/{INTERVIEW_ID}/skills",
        json=skills_from_domain,
    )
    def check_skills_reg(d):
        assert d["skills_received"] > 0
        print(f"       → {d['skills_received']} skills registered")
    test("POST interviews/{id}/skills", r, 200, check_skills_reg)
else:
    print("  [SKIP] No skills from domain selection")


# =====================================================================
print("\n" + "=" * 60)
print("  6. UPLOAD QUESTIONS (3:4:3) FOR INTERVIEW")
print("=" * 60)

TOPIC_FOR_INTERVIEW = topic_id or "T_JS_CLOSURES"

r = requests.post(
    f"{BASE}/interviews/{INTERVIEW_ID}/upload-questions",
    params={"topic_id": TOPIC_FOR_INTERVIEW, "total": 10, "company_id": COMPANY_ID},
)
def check_upload(d):
    assert d.get("total_cached", 0) > 0, "Expected cached questions"
    print(f"       → {d['total_cached']} questions cached, persisted to: {d.get('persisted_to')}")
test("POST interviews/{id}/upload-questions (3:4:3)", r, 200, check_upload)


# =====================================================================
print("\n" + "=" * 60)
print("  7. RECRUITER VIEWS")
print("=" * 60)

# 7a. Candidate view (questions only)
r = requests.get(f"{BASE}/interviews/{INTERVIEW_ID}/questions")
test("GET interviews/{id}/questions (candidate view)", r, 200,
     lambda d: print(f"       → {len(d)} questions"))

# 7b. Recruiter view (questions + answers)
r = requests.get(f"{BASE}/interviews/{INTERVIEW_ID}/recruiter")
def check_recruiter(d):
    assert "questions" in d
    if d["questions"]:
        assert "answers" in d["questions"][0], "Recruiter view should include answers"
    print(f"       → {d['total_questions']} questions with answers")
test("GET interviews/{id}/recruiter (with answers)", r, 200, check_recruiter)

# 7c. List all interviews
r = requests.get(f"{BASE}/interviews")
test("GET /interviews (list all)", r, 200,
     lambda d: print(f"       → {len(d)} interviews cached"))

# 7d. Full from MongoDB
r = requests.get(f"{BASE}/interviews/{INTERVIEW_ID}/full")
def check_full(d):
    assert d.get("interview_id") == INTERVIEW_ID
    assert d.get("job_description") is not None, "job_description should be persisted"
    print(f"       → Full doc from Mongo, JD: '{(d.get('job_description') or '')[:50]}...'")
test("GET interviews/{id}/full (MongoDB)", r, 200, check_full)


# =====================================================================
print("\n" + "=" * 60)
print("  8. CANDIDATE FLOW")
print("=" * 60)

CANDIDATE_ID = "CAND_TEST_001"

# 8a. Start interview
r = requests.post(f"{BASE}/candidate/start", json={
    "candidate_id": CANDIDATE_ID,
    "interview_id": INTERVIEW_ID,
})
session_id = None
first_question_id = None
def check_start(d):
    global session_id, first_question_id
    session_id = d["session_id"]
    assert d["total_questions"] > 0
    first_question_id = d["questions"][0]["question_id"]
    print(f"       → Session: {session_id}, {d['total_questions']} questions")
test("POST /candidate/start", r, 200, check_start)

# 8b. Submit an answer
if session_id and first_question_id:
    r = requests.post(f"{BASE}/candidate/{session_id}/answer", json={
        "question_id": first_question_id,
        "answer_text": "A closure is a function with access to its outer scope.",
        "code": "const add = (a) => (b) => a + b;",
    })
    test("POST /candidate/{id}/answer", r, 200,
         lambda d: print(f"       → Saved answer for {d['question_id']}"))

# 8c. Check status
if session_id:
    r = requests.get(f"{BASE}/candidate/{session_id}/status")
    test("GET /candidate/{id}/status", r, 200,
         lambda d: print(f"       → Status: {d['status']}, answered: {d['total_answered']}"))

# 8d. List answers
if session_id:
    r = requests.get(f"{BASE}/candidate/{session_id}/answers")
    test("GET /candidate/{id}/answers", r, 200,
         lambda d: print(f"       → {d['total_answered']} answers saved"))

# 8e. Submit interview
if session_id:
    r = requests.post(f"{BASE}/candidate/{session_id}/submit")
    def check_submit(d):
        assert d["status"] == "submitted"
        assert len(d["questions_with_answers"]) > 0
        first_q = d["questions_with_answers"][0]
        print(f"       → Submitted, {d['total_questions']} questions returned with answers")
        if first_q.get("candidate_answer"):
            print(f"       → Candidate answer attached: YES")
    test("POST /candidate/{id}/submit", r, 200, check_submit)

# 8f. Verify result (side-by-side)
if session_id:
    r = requests.post(f"{BASE}/candidate/{session_id}/verify_result")
    def check_verify(d):
        assert d["total_questions"] > 0
        first = d["results"][0]
        print(f"       → {d['total_answered']}/{d['total_questions']} answered")
        if first.get("org_answer"):
            print(f"       → Org answer present: YES")
        if first.get("candidate_answer"):
            print(f"       → Candidate answer present: YES")
    test("POST /candidate/{id}/verify_result", r, 200, check_verify)


# =====================================================================
print("\n" + "=" * 60)
print("  9. CLEANUP — Delete interview cache")
print("=" * 60)

r = requests.delete(f"{BASE}/interviews/{INTERVIEW_ID}")
test("DELETE /interviews/{id}", r, 200,
     lambda d: print(f"       → {d['status']}"))

# Verify it's gone
r = requests.get(f"{BASE}/interviews/{INTERVIEW_ID}/questions")
test("Confirm cache deleted (404)", r, 404)


# =====================================================================
print("\n" + "=" * 60)
print(f"  RESULTS:  {passed}/{total} passed,  {failed} failed")
print("=" * 60)

if failed:
    sys.exit(1)
else:
    print("\n  All tests passed!\n")
    sys.exit(0)

"""
Test: CSV Upload Endpoint (focused)
=====================================
Tests the POST /upload-questions-csv endpoint specifically:
  - Valid CSV upload with company_id
  - Verify nodes created in Neo4j via graph traversal
  - Verify company_id on questions and answers
  - Invalid file type rejection
  - Empty CSV rejection
  - Missing columns rejection

Run:  python test_files/test_csv_upload.py
"""

import requests
import os
import sys
import tempfile

BASE = "http://localhost:8000"
COMPANY_ID = "COMP_CSV_TEST"
CSV_PATH = os.path.join(os.path.dirname(__file__), "sample_questions.csv")

passed = 0
failed = 0
total  = 0


def test(name, response, expected_status=200, check_fn=None):
    global passed, failed, total
    total += 1
    try:
        assert response.status_code == expected_status, \
            f"Expected {expected_status}, got {response.status_code}: {response.text[:300]}"
        if check_fn:
            check_fn(response.json())
        passed += 1
        print(f"  [PASS] {name}")
    except AssertionError as e:
        failed += 1
        print(f"  [FAIL] {name} — {e}")


# =====================================================================
print("\n" + "=" * 60)
print("  TEST 1: Upload valid CSV")
print("=" * 60)

with open(CSV_PATH, "rb") as f:
    r = requests.post(
        f"{BASE}/upload-questions-csv",
        data={"company_id": COMPANY_ID},
        files={"file": ("sample_questions.csv", f, "text/csv")},
    )

def check_upload(d):
    assert d["status"] == "completed"
    assert d["company_id"] == COMPANY_ID
    assert d["loaded"] >= 6, f"Expected >=6, got {d['loaded']}"
    assert d["skipped"] == 0, f"Expected 0 skipped, got {d['skipped']}"
    print(f"       → loaded={d['loaded']}, skipped={d['skipped']}, total={d['total_rows']}")

test("Valid CSV upload", r, 200, check_upload)


# =====================================================================
print("\n" + "=" * 60)
print("  TEST 2: Verify graph nodes via traversal")
print("=" * 60)

# Check skills under Frontend domain
r = requests.post(
    f"{BASE}/interviews/CSV_VERIFY/domain",
    json={"domain_id": "D_FRONTEND", "job_description": "test verification"},
)
def check_frontend_skills(d):
    skill_ids = [s["skill_id"] for s in d.get("skills", [])]
    assert "S_JAVASCRIPT" in skill_ids, f"S_JAVASCRIPT not found in {skill_ids}"
    assert "S_REACT" in skill_ids, f"S_REACT not found in {skill_ids}"
    print(f"       → Frontend skills: {skill_ids}")
test("Frontend domain has JS + React skills", r, 200, check_frontend_skills)

# Check Backend domain
r = requests.post(
    f"{BASE}/interviews/CSV_VERIFY_2/domain",
    json={"domain_id": "D_BACKEND", "job_description": "test verification backend"},
)
def check_backend_skills(d):
    skill_ids = [s["skill_id"] for s in d.get("skills", [])]
    assert "S_SQL" in skill_ids, f"S_SQL not found in {skill_ids}"
    print(f"       → Backend skills: {skill_ids}")
test("Backend domain has SQL skill", r, 200, check_backend_skills)

# Topics under JavaScript
r = requests.get(f"{BASE}/skills/S_JAVASCRIPT/topics")
def check_js_topics(d):
    topic_ids = [t["topic_id"] for t in d]
    assert "T_JS_CLOSURES" in topic_ids
    assert "T_JS_DOM" in topic_ids
    print(f"       → JS topics: {topic_ids}")
test("JavaScript skill has Closures + DOM topics", r, 200, check_js_topics)

# Difficulties under Closures
r = requests.get(f"{BASE}/topics/T_JS_CLOSURES/difficulties")
def check_closures_diff(d):
    levels = [df["level"] for df in d]
    assert "Medium" in levels, f"Expected Medium in {levels}"
    print(f"       → Closures difficulties: {levels}")
test("Closures topic has Medium difficulty", r, 200, check_closures_diff)


# =====================================================================
print("\n" + "=" * 60)
print("  TEST 3: Verify company_id on questions")
print("=" * 60)

# Get questions from a known difficulty
r = requests.get(f"{BASE}/topics/T_JS_CLOSURES/difficulties")
if r.status_code == 200 and r.json():
    diff_id = r.json()[0]["difficulty_id"]
    r2 = requests.get(f"{BASE}/difficulties/{diff_id}/questions")
    def check_company_on_q(d):
        for q in d:
            assert COMPANY_ID in q.get("company_ids", []), \
                f"company_id '{COMPANY_ID}' missing from question {q['question_id']}"
        print(f"       → All {len(d)} questions have company_id '{COMPANY_ID}'")
    test("Questions have company_id in company_ids", r2, 200, check_company_on_q)

# Get answers and verify they exist
    if r2.status_code == 200 and r2.json():
        qid = r2.json()[0]["question_id"]
        r3 = requests.get(f"{BASE}/questions/{qid}/answers")
        def check_answer_exists(d):
            assert len(d) > 0, "Expected at least 1 answer"
            assert d[0].get("explanation") is not None, "Answer should have explanation"
            print(f"       → Answer: {(d[0]['explanation'] or '')[:80]}...")
        test("Answers exist with explanation", r3, 200, check_answer_exists)


# =====================================================================
print("\n" + "=" * 60)
print("  TEST 4: Re-upload same CSV (idempotent merge)")
print("=" * 60)

COMPANY_ID_2 = "COMP_CSV_REUPLOAD"
with open(CSV_PATH, "rb") as f:
    r = requests.post(
        f"{BASE}/upload-questions-csv",
        data={"company_id": COMPANY_ID_2},
        files={"file": ("sample_questions.csv", f, "text/csv")},
    )
def check_reupload(d):
    assert d["loaded"] >= 6
    print(f"       → Re-uploaded with new company_id '{COMPANY_ID_2}'")
test("Re-upload with different company_id", r, 200, check_reupload)

# Verify both company_ids are on the question now
if r.status_code == 200:
    r2 = requests.get(f"{BASE}/topics/T_JS_CLOSURES/difficulties")
    if r2.status_code == 200 and r2.json():
        diff_id = r2.json()[0]["difficulty_id"]
        r3 = requests.get(f"{BASE}/difficulties/{diff_id}/questions")
        def check_both_companies(d):
            q = d[0]
            assert COMPANY_ID in q.get("company_ids", []), f"Missing {COMPANY_ID}"
            assert COMPANY_ID_2 in q.get("company_ids", []), f"Missing {COMPANY_ID_2}"
            print(f"       → company_ids: {q['company_ids']}")
        test("Question now has BOTH company_ids", r3, 200, check_both_companies)


# =====================================================================
print("\n" + "=" * 60)
print("  TEST 5: Error cases")
print("=" * 60)

# 5a. Non-CSV file
r = requests.post(
    f"{BASE}/upload-questions-csv",
    data={"company_id": "X"},
    files={"file": ("data.txt", b"hello", "text/plain")},
)
test("Reject non-.csv file (400)", r, 400)

# 5b. Empty CSV
empty_csv = "question_id,title,description,difficulty_level,topic_id,topic_name,skill_id,skill_name,domain_id,domain_name,answer_id,explanation\n"
r = requests.post(
    f"{BASE}/upload-questions-csv",
    data={"company_id": "X"},
    files={"file": ("empty.csv", empty_csv.encode(), "text/csv")},
)
test("Reject empty CSV (400)", r, 400)

# 5c. CSV with missing columns
bad_csv = "question_id,title\nQ1,Hello\n"
r = requests.post(
    f"{BASE}/upload-questions-csv",
    data={"company_id": "X"},
    files={"file": ("bad.csv", bad_csv.encode(), "text/csv")},
)
test("Reject CSV with missing columns (400)", r, 400)


# Cleanup verify interviews
requests.delete(f"{BASE}/interviews/CSV_VERIFY")
requests.delete(f"{BASE}/interviews/CSV_VERIFY_2")


# =====================================================================
print("\n" + "=" * 60)
print(f"  RESULTS:  {passed}/{total} passed,  {failed} failed")
print("=" * 60)

if failed:
    sys.exit(1)
else:
    print("\n  All CSV upload tests passed!\n")
    sys.exit(0)

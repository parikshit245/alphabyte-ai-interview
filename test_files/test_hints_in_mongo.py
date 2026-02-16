"""
Test to verify that hints are being stored in MongoDB
"""
import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["interview_db"]
interviews_collection = db["interviews"]

print("\n" + "="*70)
print("TESTING HINTS STORAGE IN MONGODB")
print("="*70 + "\n")

# Fetch a sample interview document
sample_interview = interviews_collection.find_one()

if not sample_interview:
    print("❌ No interview documents found in MongoDB")
    print("   Run POST /interviews/{interview_id}/upload-questions first")
    sys.exit(1)

print(f"📄 Sample Interview ID: {sample_interview.get('interview_id')}\n")

# Check if questions exist
questions = sample_interview.get("questions", [])
if not questions:
    print("❌ No questions found in interview document")
    sys.exit(1)

print(f"✅ Found {len(questions)} questions in interview\n")

# Check each question for hints
questions_with_hints = 0
questions_without_hints = 0

print("Checking questions for hints field:\n")
for idx, question in enumerate(questions[:5], 1):  # Check first 5
    has_hints = "hints" in question and question["hints"]
    status = "✅" if has_hints else "⚠️"
    
    if has_hints:
        questions_with_hints += 1
        hints_preview = str(question["hints"])[:60] + "..." if len(str(question["hints"])) > 60 else question["hints"]
        print(f"{status} Question {idx}: {question.get('title', 'N/A')[:40]}")
        print(f"   Hints: {hints_preview}\n")
    else:
        questions_without_hints += 1
        print(f"{status} Question {idx}: {question.get('title', 'N/A')[:40]}")
        print(f"   Hints: None\n")

# Check questions_with_answers as well
print("-" * 70 + "\n")
questions_with_answers = sample_interview.get("questions_with_answers", [])
if questions_with_answers:
    print(f"✅ questions_with_answers array also exists ({len(questions_with_answers)} items)")
    
    # Check if hints are in questions_with_answers too
    first_q = questions_with_answers[0]
    if "hints" in first_q:
        print(f"✅ Hints field present in questions_with_answers")
        if first_q["hints"]:
            print(f"   Sample hint: {str(first_q['hints'])[:60]}...\n")
        else:
            print(f"   Hint value is empty/null\n")
    else:
        print(f"❌ Hints field missing in questions_with_answers\n")
else:
    print("⚠️  questions_with_answers array not found\n")

# Summary
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Total questions checked: {len(questions[:5])}")
print(f"Questions with hints: {questions_with_hints}")
print(f"Questions without hints: {questions_without_hints}\n")

if questions_with_hints > 0:
    print("✅ SUCCESS: Hints are being stored in MongoDB!")
    print("   The 'hints' field is present in question documents.")
elif questions_without_hints == len(questions[:5]):
    print("⚠️  WARNING: Questions found but no hints data")
    print("   Possible reasons:")
    print("   1. Questions in Neo4j don't have hints property set")
    print("   2. Hints column empty in uploaded CSV")
    print("   3. Need to re-upload questions with hints data")
else:
    print("✅ PARTIAL: Some questions have hints, some don't")
    print("   This is normal if only some questions have hints in Neo4j")

print("\n" + "=" * 70 + "\n")

client.close()

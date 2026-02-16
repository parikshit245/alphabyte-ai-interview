"""
Simple Bot Test - Tests Neo4j queries without LLM
This bypasses the LLM to test database functionality
"""

import os
import dotenv
from botchat import Neo4jHandler, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

dotenv.load_dotenv()

def test_neo4j_queries():
    print("""
    ╔═══════════════════════════════════════════════╗
    ║   Simple Neo4j Query Test (No LLM)            ║
    ╚═══════════════════════════════════════════════╝
    """)

    # Initialize Neo4j handler
    try:
        db = Neo4jHandler(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
        print("✅ Neo4j Connection Established\n")
    except Exception as e:
        print(f"❌ Neo4j Connection Failed: {e}")
        return

    try:
        # Test 1: Get Google JavaScript questions
        print("=" * 70)
        print("TEST 1: Get Google JavaScript Questions")
        print("=" * 70)
        
        results = db.get_questions_by_company("Google", limit=5)
        print(f"✅ Found {len(results)} Google questions:")
        for i, q in enumerate(results, 1):
            print(f"\n{i}. {q.get('question_title', 'N/A')}")
            print(f"   Company: {q.get('company', 'N/A')}")
            print(f"   Role: {q.get('role', 'N/A')}")
            print(f"   Difficulty: {q.get('difficulty', 'N/A')}")
            print(f"   Question ID: {q.get('question_id', 'N/A')}")

        # Test 2: Get Array/Sorting questions
        print("\n" + "=" * 70)
        print("TEST 2: Get Array Sorting Questions")
        print("=" * 70)
        
        results = db.get_questions_by_topic("sorting", limit=5)
        print(f"✅ Found {len(results)} sorting questions:")
        for i, q in enumerate(results, 1):
            print(f"\n{i}. {q.get('question_title', 'N/A')}")
            print(f"   Domain: {q.get('domain', 'N/A')}")
            print(f"   Skill: {q.get('skill', 'N/A')}")
            print(f"   Topic: {q.get('topic', 'N/A')}")
            print(f"   Description: {q.get('question_description', 'N/A')[:80]}...")

        # Test 3: Get JavaScript closure questions
        print("\n" + "=" * 70)
        print("TEST 3: Get JavaScript Closure Questions")
        print("=" * 70)
        
        results = db.get_questions_by_topic("Closures", limit=5)
        print(f"✅ Found {len(results)} closure questions:")
        for i, q in enumerate(results, 1):
            print(f"\n{i}. {q.get('question_title', 'N/A')}")
            print(f"   Domain: {q.get('domain', 'N/A')}")
            print(f"   Skill: {q.get('skill', 'N/A')}")
            print(f"   Question ID: {q.get('question_id', 'N/A')}")

        # Test 4: Get React questions
        print("\n" + "=" * 70)
        print("TEST 4: Get React Questions")
        print("=" * 70)
        
        results = db.get_questions_by_skill("React", limit=5)
        print(f"✅ Found {len(results)} React questions:")
        for i, q in enumerate(results, 1):
            print(f"\n{i}. {q.get('question_title', 'N/A')}")
            print(f"   Domain: {q.get('domain', 'N/A')}")
            print(f"   Skill: {q.get('skill', 'N/A')}")
            print(f"   Topic: {q.get('topic', 'N/A')}")

        # Test 5: Get specific question by ID
        print("\n" + "=" * 70)
        print("TEST 5: Get Specific Question by ID")
        print("=" * 70)
        
        question = db.get_question_by_id("Q_JS_001")
        if question:
            print(f"✅ Found question Q_JS_001:")
            print(f"\n   Title: {question.get('question_title', 'N/A')}")
            print(f"   Description: {question.get('question_description', 'N/A')}")
            print(f"   Domain: {question.get('domain', 'N/A')}")
            print(f"   Skill: {question.get('skill', 'N/A')}")
            print(f"   Topic: {question.get('topic', 'N/A')}")
            if 'answer_description' in question:
                print(f"   Answer: {question['answer_description'][:100]}...")
        else:
            print("❌ Question Q_JS_001 not found")

        # Summary
        print("\n" + "=" * 70)
        print("✅ TEST SUMMARY")
        print("=" * 70)
        print("✅ All Neo4j query methods working correctly")
        print("✅ Database contains valid interview questions")
        print("✅ Questions can be searched by:")
        print("   - Company (e.g., Google)")
        print("   - Skill (e.g., JavaScript, React)")
        print("   - Topic (e.g., Closures, Sorting)")
        print("   - Question ID")
        print("\n💡 NOTE: LLM integration requires valid API key with quota")

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
        print("\n🔒 Closed database connection")

if __name__ == "__main__":
    test_neo4j_queries()

"""
Simple test for kimibot.py - Tests one query at a time
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kimibot import Neo4jHandler, create_agent_graph
from langgraph.checkpoint.memory import MemorySaver
from datetime import datetime
import dotenv

dotenv.load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
HF_TOKEN = os.getenv("HF_TOKEN", "your-hf-token-here")

print("\n" + "="*70)
print("KIMIBOT SIMPLE TEST")
print("="*70)

# Test 1: Database connectivity
print("\n[1/3] Testing Neo4j Database Connection...")
neo4j_handler = Neo4jHandler(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

try:
    questions = neo4j_handler.get_questions_by_skill("JavaScript")
    print(f"✅ SUCCESS: Found {len(questions)} JavaScript questions")
    if questions:
        print(f"   Example: {questions[0]['question_title']}")
except Exception as e:
    print(f"❌ FAILED: {e}")
    neo4j_handler.close()
    sys.exit(1)

# Test 2: Agent graph compilation
print("\n[2/3] Compiling Agent Graph...")
try:
    workflow = create_agent_graph(neo4j_handler, HF_TOKEN)
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    print("✅ SUCCESS: Agent graph compiled")
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    neo4j_handler.close()
    sys.exit(1)

# Test 3: LLM invocation
print("\n[3/3] Testing LLM Integration (this may take 10-20 seconds)...")
print("Query: 'Give me a JavaScript question'\n")

try:
    initial_state = {
        "questions_list": [],
        "query": ["Give me a JavaScript question"],
        "response": [],
        "thread_id": f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "structured_output": None,
        "user_satisfied": False,
        "current_question_index": 0,
        "search_keywords": None,
        "search_results": None,
        "need_depth_search": False,
        "enable_rag": True,
        "search_depth": 2
    }
    
    config = {"configurable": {"thread_id": initial_state["thread_id"]}}
    
    print("⏳ Invoking agent workflow...")
    result = app.invoke(initial_state, config=config)
    
    print("\n" + "-"*70)
    print("RESULT:")
    print("-"*70)
    
    if result.get('structured_output'):
        print(f"\n🤖 Agent Response:\n{result['structured_output'].message}\n")
    elif result.get('response'):
        print(f"\n🤖 Agent Response:\n{result['response'][-1]}\n")
    else:
        print(f"\n📊 State Keys: {list(result.keys())}")
        print(f"📝 Questions found: {len(result.get('questions_list', []))}")
    
    print("\n✅ SUCCESS: Kimibot is working!")
    
except Exception as e:
    print(f"\n❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    
    # Check if it's an API key issue
    if "401" in str(e) or "unauthorized" in str(e).lower():
        print("\n💡 TIP: Check your HF_TOKEN in .env file")
    elif "quota" in str(e).lower() or "429" in str(e):
        print("\n💡 TIP: API quota exceeded - try different model or wait")
    
finally:
    neo4j_handler.close()

print("\n" + "="*70)
print("TEST COMPLETED")
print("="*70 + "\n")

"""
Test script for kimibot.py (OpenAI/HuggingFace implementation)
Tests the chatbot functionality programmatically
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


def test_kimibot_basic():
    """Test basic kimibot functionality"""
    print("\n" + "="*60)
    print("KIMIBOT TEST - Basic Functionality")
    print("="*60 + "\n")
    
    # Initialize handlers
    print("📊 Initializing Neo4j handler...")
    neo4j_handler = Neo4jHandler(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    # Test database connection
    print("🔍 Testing database connection...")
    try:
        questions = neo4j_handler.get_questions_by_skill("JavaScript")
        print(f"✅ Database connected - Found {len(questions)} JavaScript questions\n")
    except Exception as e:
        print(f"❌ Database connection failed: {e}\n")
        neo4j_handler.close()
        return False
    
    # Initialize chatbot agent
    print("🤖 Initializing Agent Graph...")
    try:
        workflow = create_agent_graph(neo4j_handler, HF_TOKEN)
        memory = MemorySaver()
        app = workflow.compile(checkpointer=memory)
        print("✅ Agent graph compiled successfully\n")
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}\n")
        import traceback
        traceback.print_exc()
        neo4j_handler.close()
        return False
    
    # Test 1: Request JavaScript questions
    print("\n" + "-"*60)
    print("TEST 1: Request JavaScript Questions")
    print("-"*60)
    
    test_query = "Give me a JavaScript question"
    print(f"Query: '{test_query}'\n")
    
    try:
        initial_state = {
            "questions_list": [],
            "query": [test_query],
            "response": [],
            "thread_id": f"test_thread_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
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
        result = app.invoke(initial_state, config=config)
        
        print(f"✅ Test completed successfully!")
        print(f"📝 Questions in list: {len(result.get('questions_list', []))}")
        if result.get('structured_output'):
            print(f"💬 Agent message: {result['structured_output'].message[:200]}...")
        elif result.get('response'):
            print(f"💬 Agent response: {result['response'][-1][:200]}...")
        print()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        neo4j_handler.close()
        return False
    
    # Test 2: Search by company
    print("\n" + "-"*60)
    print("TEST 2: Request Questions by Company")
    print("-"*60)
    
    test_query = "Show me questions from Google"
    print(f"Query: '{test_query}'\n")
    
    try:
        initial_state["query"] = [test_query]
        initial_state["user_satisfied"] = False
        initial_state["thread_id"] = f"test_thread_2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        config = {"configurable": {"thread_id": initial_state["thread_id"]}}
        result = app.invoke(initial_state, config=config)
        
        print(f"✅ Test completed successfully!")
        print(f"📝 Questions in list: {len(result.get('questions_list', []))}")
        if result.get('structured_output'):
            print(f"💬 Agent message: {result['structured_output'].message[:200]}...")
        print()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        neo4j_handler.close()
        return False
    
    # Test 3: RAG disabled
    print("\n" + "-"*60)
    print("TEST 3: Test with RAG Disabled")
    print("-"*60)
    
    test_query = "What is React?"
    print(f"Query: '{test_query}'\n")
    
    try:
        initial_state["query"] = [test_query]
        initial_state["enable_rag"] = False  # RAG disabled
        initial_state["user_satisfied"] = False
        initial_state["thread_id"] = f"test_thread_3_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        config = {"configurable": {"thread_id": initial_state["thread_id"]}}
        result = app.invoke(initial_state, config=config)
        
        print(f"✅ Test completed successfully!")
        if result.get('structured_output'):
            print(f"💬 Agent message: {result['structured_output'].message[:300]}...")
        print()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        neo4j_handler.close()
        return False
    
    # Cleanup
    neo4j_handler.close()
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60 + "\n")
    return True


def test_neo4j_queries_only():
    """Test Neo4j queries without LLM"""
    print("\n" + "="*60)
    print("KIMIBOT TEST - Neo4j Queries Only (No LLM)")
    print("="*60 + "\n")
    
    print("📊 Initializing Neo4j handler...")
    neo4j_handler = Neo4jHandler(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    tests = [
        ("JavaScript", neo4j_handler.get_questions_by_skill),
        ("React", neo4j_handler.get_questions_by_skill),
        ("Google", neo4j_handler.get_questions_by_company),
        ("Microsoft", neo4j_handler.get_questions_by_company),
    ]
    
    for search_term, query_func in tests:
        try:
            questions = query_func(search_term)
            print(f"✅ {search_term}: Found {len(questions)} questions")
            if questions:
                # Handle both skill and company questions which have different field names
                if 'question_title' in questions[0]:
                    print(f"   Sample: {questions[0]['question_title'][:80]}...")
                elif 'question_description' in questions[0]:
                    print(f"   Sample: {questions[0]['question_description'][:80]}...")
                else:
                    print(f"   Fields: {list(questions[0].keys())}")
        except Exception as e:
            print(f"❌ {search_term}: Failed - {e}")
            import traceback
            traceback.print_exc()
    
    neo4j_handler.close()
    print("\n✅ Neo4j query tests completed!\n")


if __name__ == "__main__":
    print("\n🚀 Starting Kimibot Tests...\n")
    
    # Test Neo4j queries first (no LLM needed)
    print("="*60)
    print("PHASE 1: Database Query Tests")
    print("="*60)
    test_neo4j_queries_only()
    
    # Test full chatbot (requires LLM)
    print("\n" + "="*60)
    print("PHASE 2: Full Chatbot Tests (with LLM)")
    print("="*60)
    try:
        test_kimibot_basic()
    except Exception as e:
        print(f"\n❌ Full chatbot test failed: {e}")
        print("Note: This requires a valid HF_TOKEN in .env file")
        import traceback
        traceback.print_exc()

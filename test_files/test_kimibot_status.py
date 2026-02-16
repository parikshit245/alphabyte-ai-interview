"""
KIMIBOT STATUS CHECK - Quick Test
==================================
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kimibot import Neo4jHandler
import dotenv

dotenv.load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
HF_TOKEN = os.getenv("HF_TOKEN", "your-hf-token-here")

print("\n" + "="*70)
print("KIMIBOT STATUS CHECK")
print("="*70 + "\n")

# Test 1: Database
print("[1] NEO4J DATABASE")
print("-" * 70)
neo4j_handler = Neo4jHandler(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

try:
    js_questions = neo4j_handler.get_questions_by_skill("JavaScript")
    react_questions = neo4j_handler.get_questions_by_skill("React")
    google_questions = neo4j_handler.get_questions_by_company("Google")
    
    print(f"  Status: WORKING")
    print(f"  - JavaScript questions: {len(js_questions)}")
    print(f"  - React questions: {len(react_questions)}")
    print(f"  - Google questions: {len(google_questions)}")
    if js_questions:
        print(f"  - Sample: {js_questions[0]['question_title']}")
    database_ok = True
except Exception as e:
    print(f"  Status: FAILED - {e}")
    database_ok = False

neo4j_handler.close()

# Test 2: LangGraph
print("\n[2] LANGGRAPH WORKFLOW")
print("-" * 70)

try:
    from kimibot import create_agent_graph
    from langgraph.checkpoint.memory import MemorySaver
    
    neo4j_handler = Neo4jHandler(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    workflow = create_agent_graph(neo4j_handler, HF_TOKEN)
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    print(f"  Status: WORKING")
    print(f"  - Workflow compiled successfully")
    print(f"  - Nodes: 6 (start, extract, depth_search, model_query, check, end)")
    langgraph_ok = True
    neo4j_handler.close()
    
except Exception as e:
    print(f"  Status: FAILED - {e}")
    langgraph_ok = False

# Test 3: LLM
print("\n[3] LLM INTEGRATION (HF ROUTER)")
print("-" * 70)

try:
    from openai import OpenAI
    
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=HF_TOKEN,
    )
    
    # Quick test call
    completion = client.chat.completions.create(
        model="moonshotai/Kimi-K2.5:novita",
        messages=[{"role": "user", "content": "Say only: test"}],
        temperature=0.7,
        max_tokens=5
    )
    response = completion.choices[0].message.content
    
    print(f"  Status: WORKING")
    print(f"  - HF Router authentication: SUCCESS")
    print(f"  - Model: moonshotai/Kimi-K2.5:novita")
    print(f"  - Test response: '{response}'")
    llm_ok = True
    
except Exception as e:
    error_str = str(e)
    if "401" in error_str or "Invalid username" in error_str:
        print(f"  Status: AUTH FAILED")
        print(f"  - Issue: Invalid HF_TOKEN")
        print(f"  - Action: Get token from https://huggingface.co/settings/tokens")
    elif "400" in error_str:
        print(f"  Status: PARTIAL")
        print(f"  - Auth works but model/request issue")
        print(f"  - Error: {error_str[:80]}")
    else:
        print(f"  Status: FAILED")  
        print(f"  - Error: {error_str[:80]}")
    llm_ok = False

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

components = [
    ("Neo4j Database", database_ok),
    ("LangGraph Workflow", langgraph_ok),
    ("LLM Integration", llm_ok),
]

for name, status in components:
    icon = "[OK]" if status else "[FAIL]"
    print(f"  {icon} {name}")

print()
all_ok = all(s for _, s in components)

if all_ok:
    print("RESULT: All systems operational!")
    print("\nKimibot is ready to use:")
    print("  - Run: python kimibot.py")
    print("  - Or import and use in your application")
    
elif database_ok and langgraph_ok and not llm_ok:
    print("RESULT: Core working, LLM needs attention")
    print("\nWhat's working:")
    print("  + Database queries")
    print("  + Agent architecture")
    print("\nWhat needs fixing:")
    print("  - LLM API authentication/configuration")
    
else:
    print("RESULT: Critical issues found")
    print("Review errors above")

print("\n" + "="*70 + "\n")

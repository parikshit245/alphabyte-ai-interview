"""
KIMIBOT TEST RESULTS - Comprehensive Report
============================================

Date: February 16, 2026
Test Type: Full System Test (LangGraph + Neo4j + OpenAI/HF Router)
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

print("\n" + "="*80)
print("KIMIBOT SYSTEM TEST REPORT")
print("="*80 + "\n")

# ====================================================================================
# SECTION 1: NEO4J DATABASE LAYER (CRITICAL PATH)
# ====================================================================================
print("┌─" + "─"*76 + "─┐")
print("│ SECTION 1: NEO4J DATABASE LAYER                                            │")
print("└─" + "─"*76 + "─┘\n")

neo4j_handler = Neo4jHandler(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
database_working = True

tests = {
    "JavaScript Skill Query": lambda: neo4j_handler.get_questions_by_skill("JavaScript"),
    "React Skill Query": lambda: neo4j_handler.get_questions_by_skill("React"),
    "Arrays Skill Query": lambda: neo4j_handler.get_questions_by_skill("Arrays"),
    "Google Company Query": lambda: neo4j_handler.get_questions_by_company("Google"),
    "Microsoft Company Query": lambda: neo4j_handler.get_questions_by_company("Microsoft"),
    "Amazon Company Query": lambda: neo4j_handler.get_questions_by_company("Amazon"),
}

database_results = {}
for test_name, test_func in tests.items():
    try:
        results = test_func()
        status = "✅ PASS" if results else "⚠️  EMPTY"
        count = len(results)
        database_results[test_name] = (status, count, None)
        
        sample = None
        if results:
            if 'question_title' in results[0]:
                sample = results[0]['question_title'][:60]
            elif 'question_description' in results[0]:
                sample = results[0]['question_description'][:60]
        
        print(f"{status:12} {test_name:30} ({count} results)")
        if sample:
            print(f"             └─ Sample: {sample}...")
            
    except Exception as e:
        database_working = False
        database_results[test_name] = ("❌ FAIL", 0, str(e))
        print(f"❌ FAIL      {test_name:30} Error: {str(e)[:40]}")

neo4j_handler.close()

# ====================================================================================
# SECTION 2: LANGGRAPH AGENT WORKFLOW
# ====================================================================================
print("\n┌─" + "─"*76 + "─┐")
print("│ SECTION 2: LANGGRAPH AGENT WORKFLOW                                        │")
print("└─" + "─"*76 + "─┘\n")

try:
    from kimibot import create_agent_graph
    from langgraph.checkpoint.memory import MemorySaver
    from datetime import datetime
    
    neo4j_handler = Neo4jHandler(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    print("Testing workflow compilation...")
    workflow = create_agent_graph(neo4j_handler, HF_TOKEN)
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    print("✅ PASS      LangGraph workflow compilation")
    print("             └─ Nodes: start→extract_keywords→depth_search→model_query")
    print("             └─        →check_satisfaction→end")
    print("             └─ Checkpointer: MemorySaver (thread-based state)")
    
    langgraph_working = True
    neo4j_handler.close()
    
except Exception as e:
    print(f"❌ FAIL      LangGraph workflow compilation")
    print(f"             └─ Error: {str(e)[:60]}")
    langgraph_working = False

# ====================================================================================
# SECTION 3: LLM INTEGRATION (HUGGING FACE ROUTER)
# ====================================================================================
print("\n┌─" + "─"*76 + "─┐")
print("│ SECTION 3: LLM INTEGRATION TEST                                            │")
print("└─" + "─"*76 + "─┘\n")

try:
    from openai import OpenAI
    
    print("Testing OpenAI client initialization...")
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=HF_TOKEN,
    )
    print("✅ PASS      OpenAI client created (HF Router endpoint)")
    
    print("\nTesting LLM API call...")
    try:
        completion = client.chat.completions.create(
            model="moonshotai/Kimi-K2.5:novita",
            messages=[{"role": "user", "content": "Say 'test' and nothing else"}],
            temperature=0.7,
            max_tokens=10
        )
        response = completion.choices[0].message.content
        print(f"✅ PASS      LLM API call successful")
        print(f"             └─ Model: moonshotai/Kimi-K2.5:novita")
        print(f"             └─ Response: {response[:60]}")
        llm_working = True
        
    except Exception as api_error:
        error_msg = str(api_error)
        print(f"❌ FAIL      LLM API call failed")
        print(f"             └─ Error: {error_msg[:60]}")
        
        if "401" in error_msg or "Invalid username or password" in error_msg:
            print(f"             └─ Issue: Invalid or expired HF_TOKEN")
            print(f"             └─ Action: Get new token from https://huggingface.co/settings/tokens")
        elif "404" in error_msg:
            print(f"             └─ Issue: Model not found or no access")
        elif "quota" in error_msg.lower() or "429" in error_msg:
            print(f"             └─ Issue: API quota exceeded")
        
        llm_working = False
        
except Exception as e:
    print(f"❌ FAIL      OpenAI client initialization")
    print(f"             └─ Error: {str(e)[:60]}")
    llm_working = False

# ====================================================================================
# SECTION 4: ENVIRONMENT CONFIGURATION
# ====================================================================================
print("\n┌─" + "─"*76 + "─┐")
print("│ SECTION 4: ENVIRONMENT CONFIGURATION                                       │")
print("└─" + "─"*76 + "─┘\n")

env_vars = {
    "NEO4J_URI": NEO4J_URI,
    "NEO4J_USER": NEO4J_USER,
    "NEO4J_PASSWORD": "***" if NEO4J_PASSWORD else "NOT SET",
    "HF_TOKEN": f"{HF_TOKEN[:15]}..." if HF_TOKEN and HF_TOKEN != "your-hf-token-here" else "NOT SET",
}

for var_name, var_value in env_vars.items():
    status = "✅" if var_value and "NOT SET" not in var_value else "❌"
    print(f"{status} {var_name:20} = {var_value}")

# ====================================================================================
# FINAL SUMMARY
# ====================================================================================
print("\n" + "="*80)
print("SUMMARY")
print("="*80 + "\n")

components = {
    "Neo4j Database Layer": database_working,
    "LangGraph Workflow": langgraph_working,
    "LLM Integration": llm_working,
}

all_working = all(components.values())

for component, status in components.items():
    icon = "✅ WORKING" if status else "❌ BLOCKED"
    print(f"{icon:15} {component}")

print("\n" + "─"*80 + "\n")

if all_working:
    print("🎉 SUCCESS: All components working! Kimibot is fully operational.")
    print("\n   You can now use:")
    print("   - python kimibot.py (interactive chat)")
    print("   - Import and use the agent in your application")
    
elif database_working and langgraph_working and not llm_working:
    print("⚠️  PARTIAL: Core infrastructure working, LLM blocked by authentication")
    print("\n   Working:")
    print("   ✅ Neo4j queries retrieving questions")
    print("   ✅ LangGraph workflow compiles successfully")
    print("   ✅ Agent architecture ready")
    print("\n   Blocked:")
    print("   ❌ LLM API calls (HF Router authentication failing)")
    print("\n   Next Steps:")
    print("   1. Get valid HF token: https://huggingface.co/settings/tokens")
    print("   2. Update .env file: HF_TOKEN=your_new_token")
    print("   3. Restart kimibot")
    print("\n   Alternative:")
    print("   - Use botchat.py with Gemini (if you have quota)")
    print("   - Or modify kimibot.py to use different LLM provider")
    
else:
    print("❌ FAILURE: Critical components not working")
    print("\n   Review errors above and fix configuration")

print("\n" + "="*80 + "\n")

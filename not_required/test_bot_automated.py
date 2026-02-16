
import os
import dotenv
from datetime import datetime
from botchat import Neo4jHandler, create_agent_graph, AgentState, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, GOOGLE_API_KEY
from langgraph.checkpoint.memory import MemorySaver

# Load environment variables
dotenv.load_dotenv()

def test_chatbot():
    print("""
    ╔═══════════════════════════════════════════════╗
    ║   Automated Test for Interview Prep Agent     ║
    ╚═══════════════════════════════════════════════╝
    """)

    # Initialize Neo4j handler
    try:
        neo4j_handler = Neo4jHandler(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
        print("✅ Neo4j Connection Established")
    except Exception as e:
        print(f"❌ Neo4j Connection Failed: {e}")
        return

    try:
        # Create the agent graph
        workflow = create_agent_graph(neo4j_handler, GOOGLE_API_KEY)
        
        # Compile the graph with memory
        memory = MemorySaver()
        app = workflow.compile(checkpointer=memory)
        print("✅ Graph Compiled Successfully")
        
        # Initialize state
        thread_id = f"test_thread_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        initial_state = {
            "questions_list": [],
            "query": [],
            "response": [],
            "thread_id": thread_id,
            "structured_output": None,
            "user_satisfied": False,
            "current_question_index": 0,
            "search_keywords": None,
            "search_results": None,
            "need_depth_search": False,
            "enable_rag": True,
            "search_depth": 2
        }
        
        config = {"configurable": {"thread_id": thread_id}}
        
        # Define test inputs (updated to match actual DB content)
        test_inputs = [
            "Give me Google JavaScript questions",
            "I want to practice Array sorting questions",
            "What is a closure?",
            "Show me React interview questions",
            "Thanks, exit"
        ]

        current_state = initial_state

        for i, user_input in enumerate(test_inputs, 1):
            print(f"\n\n--- Test Case {i} ---")
            print(f"👤 User Input: {user_input}")
            
            # Update state with new query
            current_state["query"] = [user_input]
            current_state["user_satisfied"] = False
            
            try:
                # Run the graph
                result = app.invoke(current_state, config=config)
                
                # Print Result Summary
                structured_out = result.get("structured_output")
                if structured_out:
                    print(f"🤖 Agent Response: {structured_out.message}")
                    print(f"   Next Action: {structured_out.next_action}")
                    
                    if structured_out.questions_provided:
                        print(f"   📚 Questions Found: {len(structured_out.questions_provided)}")
                        for q in structured_out.questions_provided:
                            print(f"      - {q.question}")
                            
                    if structured_out.feedback:
                        print(f"   📊 Feedback Score: {structured_out.feedback.score}")
                
                # Check search results if any
                if result.get("search_results") and result["search_results"].total_results > 0:
                     print(f"   🔍 DB Results Used: {result['search_results'].total_results}")

                # Update state for next turn
                current_state = result

            except Exception as e:
                print(f"❌ Error executing test case {i}: {e}")
                import traceback
                traceback.print_exc()

    finally:
        # Cleanup
        neo4j_handler.close()
        print("\n🔒 Closed database connection")

if __name__ == "__main__":
    test_chatbot()

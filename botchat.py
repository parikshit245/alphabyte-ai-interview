"""
Interview Preparation Agent System using LangGraph and Neo4j

This agent system helps users prepare for interview questions by:
- Managing a conversation state with questions, answers, and evaluations
- Querying Neo4j database for interview questions
- Providing feedback and guidance
- Supporting multi-turn conversations with thread management
"""

import os
from typing import List, Annotated, Literal, Optional
from typing_extensions import TypedDict
from datetime import datetime
import operator
import dotenv

dotenv.load_dotenv()

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from neo4j import GraphDatabase


# ============================================================================
# CONFIGURATION
# ============================================================================

# Neo4j Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")


# ============================================================================
# PYDANTIC MODELS FOR STRUCTURED OUTPUT
# ============================================================================

class QuestionAnswer(BaseModel):
    """Structure for a single question-answer pair"""
    question: str = Field(description="The interview question")
    question_id: str = Field(description="Unique identifier for the question")
    candidate_answer: Optional[str] = Field(default=None, description="User's answer to the question")
    org_answer: Optional[str] = Field(default=None, description="Original/correct answer from database")


class FeedbackResponse(BaseModel):
    """Structured feedback on user's answer"""
    evaluation: str = Field(description="Evaluation of the candidate's answer")
    strengths: List[str] = Field(description="Strong points in the answer")
    improvements: List[str] = Field(description="Areas for improvement")
    score: int = Field(description="Score out of 10", ge=0, le=10)
    follow_up_suggestions: List[str] = Field(description="Suggestions for follow-up learning")
    

class SearchKeywords(BaseModel):
    domain: Optional[str] = Field(None, description="The industry or domain related to the query")
    skills: List[str] = Field(default_factory=list, description="List of technical skills or qualifications mentioned")
    Topic: Optional[str] = Field(None, description="The specific ID of the company")
    company_name: Optional[str] = Field(None, description="The name of the company")
    domain_res: Optional[List[dict]] = Field(default=None, description="Results from domain-based search")
    topic_results: Optional[List[dict]] = Field(default=None, description="Results from topic-based search")
    skill_results: Optional[List[dict]] = Field(default=None, description="Results from skill-based search")
    company_results: Optional[List[dict]] = Field(default=None, description="Results from company-based search")
    merger_results: Optional[dict] = Field(default=None, description="Merged search results")

class AgentResponse(BaseModel):
    """Structured output from the agent"""
    message: str = Field(description="Main response message to the user")
    questions_provided: Optional[List[QuestionAnswer]] = Field(default=None, description="Questions provided in this response")
    feedback: Optional[FeedbackResponse] = Field(default=None, description="Feedback on user's answer if applicable")
    next_action: Literal["continue", "end", "provide_question", "evaluate_answer"] = Field(
        description="Suggested next action"
    )


# ============================================================================
# STATE DEFINITION
# ============================================================================

class AgentState(TypedDict):
    """
    State of the interview preparation agent
    
    Attributes:
        questions_list: List of [question, question_id, candidate_answer, org_answer]
        query: User's latest query (annotated to accumulate)
        response: Agent's response (annotated to accumulate)
        thread_id: Unique thread identifier for conversation persistence
        structured_output: Pydantic BaseModel output
        user_satisfied: Flag indicating if user is satisfied
        current_question_index: Index of current question being worked on
    """
    questions_list: List[List[Optional[str]]]  # [[question, question_id, candidate_answer, org_answer]]
    query: Annotated[List[str], operator.add]  # Accumulate queries
    response: Annotated[List[str], operator.add]  # Accumulate responses
    thread_id: str
    structured_output: Optional[AgentResponse]
    user_satisfied: bool
    current_question_index: int


# ============================================================================
# NEO4J DATABASE HANDLER
# ============================================================================

class Neo4jHandler:
    """Handler for Neo4j database operations"""
    
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        """Close the database connection"""
        self.driver.close()
    
    def get_questions_by_domain(self, SearchKeywords, domain_name: str, limit: int = 5) -> SearchKeywords:
        """Fetch questions by domain"""
        domain_name = SearchKeywords.domain if SearchKeywords.domain else domain_name
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (d:Domain)-[:HAS_SKILL]->(s:Skill)
                      -[:HAS_TOPIC]->(t:Topic)
                      -[:HAS_DIFFICULTY]->(diff:Difficulty)
                      -[:HAS_QUESTION]->(q:Question)
                WHERE toLower(d.domain_name) CONTAINS toLower($domain_name)
                RETURN d.domain_name AS domain,
                       s.skill_name AS skill,
                       t.topic_name AS topic,
                       q.question_id AS question_id,
                       q.question_title AS question_title
                LIMIT $limit
                """,
                domain_name=domain_name,
                limit=limit
            )
            domain_results = [record.data() for record in result]
            return {
                "domain_res": domain_results
            }
    
    def get_questions_by_topic(self, SearchKeywords, topic_name: str, limit: int = 5) -> SearchKeywords:
        """Fetch questions by topic"""
        topic_name = SearchKeywords.topic_name if SearchKeywords.topic_name else topic_name
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (d:Domain)-[:HAS_SKILL]->(s:Skill)-[:HAS_TOPIC]->(t:Topic)
                      -[:HAS_DIFFICULTY]->(diff:Difficulty)
                      -[:HAS_QUESTION]->(q:Question)
                WHERE toLower(t.topic_name) CONTAINS toLower($topic_name)
                RETURN d.domain_name AS domain,
                       s.skill_name AS skill,
                       t.topic_name AS topic,
                       q.question_id AS question_id,
                       q.question_title AS question_title
                LIMIT $limit
                """,
                topic_name=topic_name,
                limit=limit
            )
            topic_results = [record.data() for record in result]
            return {
                "topic_results": topic_results
            }

    def get_questions_by_skill(self, SearchKeywords, skill_name: str, limit: int = 5) -> SearchKeywords:
        """Fetch questions by skill"""
        skill_name = SearchKeywords.skills[0] if SearchKeywords.skills else skill_name
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (d:Domain)-[:HAS_SKILL]->(s:Skill)-[:HAS_TOPIC]->(t:Topic)
                      -[:HAS_DIFFICULTY]->(diff:Difficulty)
                      -[:HAS_QUESTION]->(q:Question)
                WHERE toLower(s.skill_name) CONTAINS toLower($skill_name)
                RETURN d.domain_name AS domain,
                       s.skill_name AS skill,
                       t.topic_name AS topic,
                       q.question_id AS question_id,
                       q.question_title AS question_title
                LIMIT $limit
                """,
                skill_name=skill_name,
                limit=limit
            )
            skill_results = [record.data() for record in result]
            return {
                "skill_res": skill_results
            }

    def get_questions_by_company(self, SearchKeywords, company_name: str, limit: int = 5) -> SearchKeywords:
        """Fetch questions asked by a specific company"""
        company_name = SearchKeywords.company_name if SearchKeywords.company_name else company_name
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (c:Company)-[:HAS_DOMAIN]->(cd:CompanyDomain)
                      -[:HAS_ROLE]->(cr:CompanyRole)-[:ASKS_QUESTION]->(cq:CompanyQuestion)
                WHERE toLower(c.company_name) CONTAINS toLower($company_name)
                RETURN c.company_name AS company,
                       cd.domain_name AS domain,
                       cr.role_name AS role,
                       cq.comp_question_id AS question_id,
                       cq.comp_question_title AS question_title
                LIMIT $limit
                """,
                company_name=company_name,
                limit=limit
            )
            company_results = [record.data() for record in result]
            return {
                "company_res": company_results
            }

    def merge_serach_results(self, SearchKeywords) -> SearchKeywords:
        """Merge search results into SearchKeywords model"""
        # This function can be expanded to merge results from multiple queries
        # For simplicity, we will just return the SearchKeywords as is for now
        merged_results = {
            "domain_res": SearchKeywords.domain_res,
            "topic_results": SearchKeywords.topic_results,
            "skill_results": SearchKeywords.skill_results,
            "company_results": SearchKeywords.company_results,
            
        }
        return {
            "merger_res": merged_results
        }

    
    def get_question_by_id(self, question_id: str) -> Optional[dict]:
        """Fetch a specific question by ID"""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (q:Question {question_id: $question_id})-[:HAS_ANSWER]->(a:Answer)
                RETURN q.question_id AS question_id,
                       q.question_title AS question_title,
                       q.question_description AS question_description,
                       q.question_hints AS question_hints,
                       q.question_example AS question_example,
                       a.answer_explanation AS answer_explanation,
                       a.answer_code AS answer_code
                """,
                question_id=question_id
            )
            record = result.single()
            return record.data() if record else None
    
    def get_questions_by_difficulty(self, difficulty_level: str, limit: int = 5) -> List[dict]:
        """Fetch questions by difficulty level"""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (diff:Difficulty {difficulty_level: $difficulty_level})
                      -[:HAS_QUESTION]->(q:Question)-[:HAS_ANSWER]->(a:Answer)
                RETURN q.question_id AS question_id,
                       q.question_title AS question_title,
                       q.question_description AS question_description,
                       a.answer_explanation AS answer_explanation,
                       diff.difficulty_level AS difficulty
                LIMIT $limit
                """,
                difficulty_level=difficulty_level,
                limit=limit
            )
            return [record.data() for record in result]


# ============================================================================
# AGENT NODES
# ============================================================================

class InterviewPrepAgent:
    """Main agent class for interview preparation"""
    
    def __init__(self, neo4j_handler: Neo4jHandler, openai_api_key: str):
        self.db = neo4j_handler
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7,
            api_key=openai_api_key
        )
        self.structured_llm = self.llm.with_structured_output(AgentResponse)
    
    def start_node(self, state: AgentState) -> AgentState:
        """Initialize the conversation"""
        print("\n🚀 Starting Interview Prep Agent...")
        
        if not state.get("thread_id"):
            state["thread_id"] = f"thread_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            print(f"📋 Created thread: {state['thread_id']}")
        
        if not state.get("questions_list"):
            state["questions_list"] = []
        
        if not state.get("current_question_index"):
            state["current_question_index"] = 0
        
        return state
    
    def model_query_node(self, state: AgentState) -> AgentState:
        """Process user query using LLM"""
        print("\n🤖 Processing query...")
        
        # Get the latest user query
        latest_query = state["query"][-1] if state["query"] else ""
        
        # Build context from conversation history
        context = self._build_context(state)
        
        # Detect intent and prepare prompt
        prompt = self._prepare_prompt(latest_query, context, state)
        
        # Get structured response from LLM
        try:
            structured_response: AgentResponse = self.structured_llm.invoke(prompt)
            
            # Update state based on response
            state["structured_output"] = structured_response
            state["response"] = [structured_response.message]
            
            # Handle different action types
            if structured_response.next_action == "provide_question":
                state = self._handle_question_provision(state, structured_response, latest_query)
            elif structured_response.next_action == "evaluate_answer":
                state = self._handle_answer_evaluation(state, structured_response)
            
            print(f"✅ Response generated: {structured_response.next_action}")
            
        except Exception as e:
            print(f"❌ Error in model query: {e}")
            state["response"] = [f"I encountered an error processing your request: {str(e)}"]
            state["structured_output"] = AgentResponse(
                message=f"Error: {str(e)}",
                next_action="continue"
            )
        
        return state
    
    def _build_context(self, state: AgentState) -> str:
        """Build conversation context"""
        context_parts = []
        
        # Add conversation history
        if len(state.get("query", [])) > 1:
            context_parts.append("Conversation History:")
            for i, (q, r) in enumerate(zip(state["query"][:-1], state["response"][:-1]), 1):
                context_parts.append(f"User {i}: {q}")
                context_parts.append(f"Agent {i}: {r}")
        
        # Add current questions
        if state["questions_list"]:
            context_parts.append("\nCurrent Questions in Session:")
            for i, q_data in enumerate(state["questions_list"], 1):
                question, q_id, candidate_ans, org_ans = q_data
                context_parts.append(f"{i}. {question} (ID: {q_id})")
                if candidate_ans:
                    context_parts.append(f"   User's answer: {candidate_ans}")
        
        return "\n".join(context_parts)
    
    def _prepare_prompt(self, query: str, context: str, state: AgentState) -> str:
        """Prepare the prompt for LLM"""
        return f"""You are an expert interview preparation assistant. Your role is to:
1. Help users practice interview questions
2. Provide detailed feedback on their answers
3. Suggest relevant questions based on their needs
4. Offer guidance and tips for improvement

Context:
{context}

Current User Query: {query}

Thread ID: {state['thread_id']}

Based on the user's query, determine the appropriate action:
- If they're requesting questions (mention: company, domain, difficulty, topic), respond with next_action="provide_question"
- If they're providing an answer to a question, respond with next_action="evaluate_answer"
- If they want to continue or have general queries, respond with next_action="continue"
- If they indicate they're done or satisfied, respond with next_action="end"

Provide a helpful, encouraging response that guides them through their interview preparation.
"""
    
    def _handle_question_provision(self, state: AgentState, response: AgentResponse, query: str) -> AgentState:
        """Handle providing questions to the user"""
        # Parse query for intent
        query_lower = query.lower()
        questions = []
        
        try:
            if "company" in query_lower:
                # Extract company name (simplified - could use NER)
                company_name = self._extract_entity(query, "company")
                if company_name:
                    questions = self.db.get_questions_by_company(company_name)
            elif "domain" in query_lower:
                domain_name = self._extract_entity(query, "domain")
                if domain_name:
                    questions = self.db.get_questions_by_domain(domain_name)
            elif any(word in query_lower for word in ["easy", "medium", "hard"]):
                difficulty = "Easy" if "easy" in query_lower else "Medium" if "medium" in query_lower else "Hard"
                questions = self.db.get_questions_by_difficulty(difficulty)
            
            # Add questions to state
            for q in questions:
                question_text = q.get("question_title") or q.get("question_description", "")
                question_id = q.get("question_id", "")
                org_answer = q.get("answer_explanation", "")
                
                state["questions_list"].append([question_text, question_id, None, org_answer])
            
            print(f"📚 Added {len(questions)} questions to session")
            
        except Exception as e:
            print(f"⚠️ Error fetching questions: {e}")
        
        return state
    
    def _handle_answer_evaluation(self, state: AgentState, response: AgentResponse) -> AgentState:
        """Handle evaluation of user's answer"""
        # Find the current question being answered
        if state["questions_list"] and state["current_question_index"] < len(state["questions_list"]):
            current_q = state["questions_list"][state["current_question_index"]]
            
            # Extract user's answer from the latest query
            user_answer = state["query"][-1] if state["query"] else ""
            
            # Update the candidate answer
            current_q[2] = user_answer
            
            print(f"✍️ Recorded answer for question {state['current_question_index'] + 1}")
            
            # Move to next question
            state["current_question_index"] += 1
        
        return state
    
    def _extract_entity(self, text: str, entity_type: str) -> Optional[str]:
        """Simple entity extraction (can be enhanced with NER)"""
        text_lower = text.lower()
        
        if entity_type == "company":
            # Common company names
            companies = ["google", "amazon", "microsoft", "apple", "facebook", "meta", "netflix", "tesla"]
            for company in companies:
                if company in text_lower:
                    return company.capitalize()
        
        elif entity_type == "domain":
            # Common domains
            domains = ["algorithms", "data structures", "system design", "machine learning", 
                      "web development", "database", "networking"]
            for domain in domains:
                if domain in text_lower:
                    return domain.title()
        
        return None
    
    def depth_search_node(self, state: AgentState) -> AgentState:
            """
            NEW NODE: Perform Graph RAG depth search
            
            This node implements Graph RAG by:
            1. Traversing the Neo4j graph at specified depth
            2. Extracting rich contextual information
            3. Identifying patterns and relationships
            4. Generating expert insights
            """
            print("\n🔬 Executing Graph RAG Depth Search Node...")
            """
            Node that performs depth research by first extracting keywords
            and then searching the database (db search currently empty).
            """
            print("---DEPTH RESEARCH NODE---")
            question = state["question"]
            
            # 1. Extract Keywords using the LLM with structured output
            print("---EXTRACTING KEYWORDS---")
            structured_llm = self.llm.with_structured_output(SearchKeywords)
            
            # helper prompt to ensure extraction focuses on the right entities
            extraction_prompt = f"""
            Extract the following details from the user's query: 
            - Domain/Industry
            - Specific Skills
            - Company Name
            - Company ID (if present)
            
            User Query: {question}
            """
            
            keywords_data = structured_llm.invoke(extraction_prompt)
            
            if not state.get("enable_rag", True):
                print("  ⏭️  Graph RAG disabled, skipping...")
                return state
            
            # Get the latest query for context
            latest_query = state["query"][-1] if state["query"] else ""
            depth = state.get("search_depth", 2)
            
            # Perform Graph RAG depth search
            # Note: graph_rag_depth_search is hypothetical here as the method doesn't exist in Neo4jHandler yet
            # Using the new methods implemented instead:
            
            # Execute searches based on extracted keywords
            if keywords_data.domain:
                keywords_data = self.db.get_questions_by_domain(keywords_data, keywords_data.domain)
            if keywords_data.skills:
                keywords_data = self.db.get_questions_by_skill(keywords_data, keywords_data.skills[0])
            if keywords_data.company_name:
                keywords_data = self.db.get_questions_by_company(keywords_data, keywords_data.company_name)
            # if keywords_data.topic_name: # assuming topic might be extracted
            #    keywords_data = self.db.get_questions_by_topic(keywords_data, keywords_data.topic_name)

            # Merge results
            keywords_data = self.db.merge_serach_results(keywords_data)
            
            # Generate insights using LLM with graph context
            insights_prompt = f"""Based on the following graph analysis, generate expert insights:

    Query: {latest_query}

    Graph Context:
    {keywords_data.merger_results}

    Generate structured insights for the user's interview preparation.
    """
            
            try:
                # Use structured LLM to generate insights
                # Assuming we want AgentResponse structure here as output
                insights_response = self.structured_llm.invoke(insights_prompt)
                
                state["structured_output"] = insights_response
                state["response"] = [insights_response.message]
                
            except Exception as e:
                print(f"  ⚠️  Error generating insights: {e}")
            
            print("  📊 Graph RAG analysis complete")
            return state    

    def check_satisfaction_node(self, state: AgentState) -> AgentState:
        """Check if user is satisfied with the response"""
        print("\n🔍 Checking user satisfaction...")
        
        # Check for satisfaction keywords
        latest_query = state["query"][-1].lower() if state["query"] else ""
        
        satisfaction_keywords = ["thanks", "thank you", "done", "finished", "exit", "bye", "good"]
        continuation_keywords = ["more", "another", "next", "continue", "help", "question"]
        
        if any(keyword in latest_query for keyword in satisfaction_keywords):
            state["user_satisfied"] = True
            print("✅ User appears satisfied")
        elif any(keyword in latest_query for keyword in continuation_keywords):
            state["user_satisfied"] = False
            print("🔄 User wants to continue")
        elif "depth" in latest_query or "research" in latest_query: # Simple keyword check for depth
            print("---DECISION: NEED MORE DEPTH RESEARCH---")
            state["next_step"] = "depth_research"
            return state
        else:
            # Default to not satisfied (continue conversation)
            state["user_satisfied"] = False
        
        return state
    
    def end_node(self, state: AgentState) -> AgentState:
        """End the conversation"""
        print("\n🎯 Ending conversation...")
        
        # Generate summary
        summary_parts = [
            "\n" + "="*50,
            "📊 INTERVIEW PREP SESSION SUMMARY",
            "="*50,
            f"\nThread ID: {state['thread_id']}",
            f"Total Questions Covered: {len(state['questions_list'])}",
            f"Questions Answered: {sum(1 for q in state['questions_list'] if q[2] is not None)}",
        ]
        
        if state["questions_list"]:
            summary_parts.append("\n📝 Questions in this session:")
            for i, q_data in enumerate(state["questions_list"], 1):
                question, q_id, candidate_ans, _ = q_data
                status = "✅ Answered" if candidate_ans else "⏳ Not answered"
                summary_parts.append(f"{i}. {question[:60]}... - {status}")
        
        summary_parts.append("\n" + "="*50)
        summary_parts.append("Thank you for using Interview Prep Agent! Good luck! 🚀")
        summary_parts.append("="*50 + "\n")
        
        summary = "\n".join(summary_parts)
        print(summary)
        
        state["response"].append(summary)
        
        return state


# ============================================================================
# GRAPH CONSTRUCTION
# ============================================================================

def create_agent_graph(neo4j_handler: Neo4jHandler, openai_api_key: str) -> StateGraph:
    """Create and configure the LangGraph workflow"""
    
    agent = InterviewPrepAgent(neo4j_handler, openai_api_key)
    
    # Initialize the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("start", agent.start_node)
    workflow.add_node("model_query", agent.model_query_node)
    workflow.add_node("depth_search", agent.depth_search_node)
    workflow.add_node("check_satisfaction", agent.check_satisfaction_node)
    workflow.add_node("end", agent.end_node)
    
    # Add edges
    workflow.add_edge(START, "start")
    workflow.add_edge("start", "model_query")
    workflow.add_edge("model_query", "check_satisfaction")
    workflow.add_edge("depth_search", "check_satisfaction")
    
    # Conditional routing based on user satisfaction
    def route_after_satisfaction(state: AgentState) -> Literal["model_query", "end", "depth_search"]:
        if state.get("user_satisfied", False):
            return "end"
        # We need to know if depth search was requested. 
        # Assuming check_satisfaction_node sets a flag or returns a specific value in state.
        # But here check_satisfaction_node returns AgentState.
        # The logic inside check_satisfaction_node was printing "NEED MORE DEPTH RESEARCH".
        # We need a field in state to hold this decision.
        if state.get("next_step") == "depth_research":
             return "depth_search"
        return "model_query"
    
    workflow.add_conditional_edges(
        "check_satisfaction",
        route_after_satisfaction,
        {
            "model_query": "model_query",
            "end": "end",
            "depth_search": "depth_search"
        }
    )
    
    workflow.add_edge("end", END)
    
    return workflow


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    print("""
    ╔═══════════════════════════════════════════════╗
    ║   Interview Preparation Agent System          ║
    ║   Powered by LangGraph + Neo4j + OpenAI       ║
    ╚═══════════════════════════════════════════════╝
    """)
    
    # Initialize Neo4j handler
    neo4j_handler = Neo4jHandler(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    try:
        # Create the agent graph
        workflow = create_agent_graph(neo4j_handler, OPENAI_API_KEY)
        
        # Compile the graph with memory
        memory = MemorySaver()
        app = workflow.compile(checkpointer=memory)
        
        # Initialize state
        initial_state: AgentState = {
            "questions_list": [],
            "query": [],
            "response": [],
            "thread_id": f"thread_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "structured_output": None,
            "user_satisfied": False,
            "current_question_index": 0
        }
        
        config = {"configurable": {"thread_id": initial_state["thread_id"]}}
        
        print("\n💬 Chat with the Interview Prep Agent (type 'exit' to quit)\n")
        
        # Interactive loop
        while True:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\n👋 Goodbye! Good luck with your interviews!")
                break
            
            # Add query to state
            initial_state["query"] = [user_input]
            initial_state["user_satisfied"] = False
            
            # Run the graph
            try:
                result = app.invoke(initial_state, config=config)
                
                # Display response
                if result.get("structured_output"):
                    print(f"\n🤖 Agent: {result['structured_output'].message}\n")
                    
                    # Display questions if provided
                    if result['structured_output'].questions_provided:
                        print("📚 Questions for you:\n")
                        for i, q in enumerate(result['structured_output'].questions_provided, 1):
                            print(f"{i}. {q.question}")
                        print()
                    
                    # Display feedback if provided
                    if result['structured_output'].feedback:
                        feedback = result['structured_output'].feedback
                        print(f"📊 Evaluation Score: {feedback.score}/10\n")
                        print(f"💪 Strengths: {', '.join(feedback.strengths)}")
                        print(f"📈 Areas for Improvement: {', '.join(feedback.improvements)}\n")
                
                # Update state for next iteration
                initial_state = result
                
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
                continue
    
    finally:
        # Cleanup
        neo4j_handler.close()
        print("\n🔒 Closed database connection")


if __name__ == "__main__":
    # Example usage
    main()


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

"""
Example Interactions:

1. Request questions by company:
   User: "Give me some Google interview questions"
   Agent: Fetches questions from Neo4j where company = "Google"

2. Request questions by domain:
   User: "I want to practice algorithms questions"
   Agent: Fetches questions from the "Algorithms" domain

3. Request questions by difficulty:
   User: "Show me some easy questions to start with"
   Agent: Fetches questions with difficulty = "Easy"

4. Answer a question:
   User: "The time complexity is O(n log n) because..."
   Agent: Evaluates the answer and provides feedback

5. Continue conversation:
   User: "Can you give me more questions on the same topic?"
   Agent: Continues fetching relevant questions

6. End session:
   User: "Thanks, that's all for today"
   Agent: Ends session and shows summary
"""
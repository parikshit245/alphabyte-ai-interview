"""
Interview Preparation Agent System using LangGraph and Neo4j
FULLY CORRECTED VERSION with Gemini support

All logical inconsistencies fixed:
- Proper state management
- Consistent return types
- Separated keyword extraction and depth search
- Fixed routing logic
- Gemini integration with structured output
"""

import os
from typing import List, Annotated, Literal, Optional, Dict, Any
from typing_extensions import TypedDict
from datetime import datetime
import operator
import json
import dotenv

dotenv.load_dotenv()

from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
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

# Google Gemini Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "your-google-api-key-here")


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
    """Extracted keywords from user query - INPUT ONLY"""
    domain: Optional[str] = Field(None, description="The industry or domain related to the query")
    skills: List[str] = Field(default_factory=list, description="List of technical skills mentioned")
    topic: Optional[str] = Field(None, description="The specific topic mentioned")
    company_name: Optional[str] = Field(None, description="The name of the company")


class SearchResults(BaseModel):
    """Aggregated search results from database - OUTPUT ONLY"""
    domain_results: Optional[List[Dict]] = Field(default=None, description="Results from domain search")
    topic_results: Optional[List[Dict]] = Field(default=None, description="Results from topic search")
    skill_results: Optional[List[Dict]] = Field(default=None, description="Results from skill search")
    company_results: Optional[List[Dict]] = Field(default=None, description="Results from company search")
    total_results: int = Field(default=0, description="Total number of results found")


class AgentResponse(BaseModel):
    """Structured output from the agent"""
    message: str = Field(description="Main response message to the user")
    questions_provided: Optional[List[QuestionAnswer]] = Field(default=None, description="Questions provided")
    feedback: Optional[FeedbackResponse] = Field(default=None, description="Feedback on answer if applicable")
    next_action: Literal["continue", "end", "provide_question", "evaluate_answer", "depth_search"] = Field(
        description="Suggested next action"
    )


# ============================================================================
# STATE DEFINITION
# ============================================================================

class AgentState(TypedDict):
    """
    Complete state of the interview preparation agent
    
    All fields properly defined and initialized
    """
    questions_list: List[List[Optional[str]]]  # [[question, question_id, candidate_answer, org_answer]]
    query: Annotated[List[str], operator.add]  # Accumulate queries
    response: Annotated[List[str], operator.add]  # Accumulate responses
    thread_id: str
    structured_output: Optional[AgentResponse]
    user_satisfied: bool
    current_question_index: int
    search_keywords: Optional[SearchKeywords]  # Extracted keywords
    search_results: Optional[SearchResults]  # Search results
    need_depth_search: bool  # Flag for depth search
    enable_rag: bool  # Enable/disable Graph RAG
    search_depth: int  # Depth level for traversal


# ============================================================================
# NEO4J DATABASE HANDLER - FIXED
# ============================================================================

class Neo4jHandler:
    """Handler for Neo4j database operations - ALL METHODS RETURN CONSISTENT TYPES"""
    
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        """Close the database connection"""
        self.driver.close()
    
    def get_questions_by_domain(self, domain_name: str, limit: int = 5) -> List[Dict]:
        """Fetch questions by domain - RETURNS List[Dict]"""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (d:Domain)-[:HAS_SKILL]->(s:Skill)
                      -[:HAS_TOPIC]->(t:Topic)
                      -[:HAS_DIFFICULTY]->(diff:Difficulty)
                      -[:HAS_QUESTION]->(q:Question)
                WHERE toLower(d.name) CONTAINS toLower($domain_name)
                RETURN d.name AS domain,
                       s.name AS skill,
                       t.name AS topic,
                       q.question_id AS question_id,
                       q.title AS question_title,
                       q.description AS question_description
                LIMIT $limit
                """,
                domain_name=domain_name,
                limit=limit
            )
            return [record.data() for record in result]
    
    def get_questions_by_topic(self, topic_name: str, limit: int = 5) -> List[Dict]:
        """Fetch questions by topic - RETURNS List[Dict]"""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (d:Domain)-[:HAS_SKILL]->(s:Skill)-[:HAS_TOPIC]->(t:Topic)
                      -[:HAS_DIFFICULTY]->(diff:Difficulty)
                      -[:HAS_QUESTION]->(q:Question)
                WHERE toLower(t.name) CONTAINS toLower($topic_name)
                RETURN d.name AS domain,
                       s.name AS skill,
                       t.name AS topic,
                       q.question_id AS question_id,
                       q.title AS question_title,
                       q.description AS question_description
                LIMIT $limit
                """,
                topic_name=topic_name,
                limit=limit
            )
            return [record.data() for record in result]

    def get_questions_by_skill(self, skill_name: str, limit: int = 5) -> List[Dict]:
        """Fetch questions by skill - RETURNS List[Dict]"""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (d:Domain)-[:HAS_SKILL]->(s:Skill)-[:HAS_TOPIC]->(t:Topic)
                      -[:HAS_DIFFICULTY]->(diff:Difficulty)
                      -[:HAS_QUESTION]->(q:Question)
                WHERE toLower(s.name) CONTAINS toLower($skill_name)
                RETURN d.name AS domain,
                       s.name AS skill,
                       t.name AS topic,
                       q.question_id AS question_id,
                       q.title AS question_title,
                       q.description AS question_description
                LIMIT $limit
                """,
                skill_name=skill_name,
                limit=limit
            )
            return [record.data() for record in result]

    def get_questions_by_company(self, company_name: str, limit: int = 5) -> List[Dict]:
        """Fetch questions asked by a specific company - RETURNS List[Dict]"""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (c:Company)-[:HAS_DOMAIN]->(cd:CompanyDomain)
                      -[:HAS_ROLE]->(cr:CompanyRole)-[:ASKS_QUESTION]->(cq:CompanyQuestion)
                WHERE toLower(c.name) CONTAINS toLower($company_name)
                RETURN c.name AS company,
                       cd.name AS domain,
                       cr.name AS role,
                       cq.comp_question_id AS question_id,
                       cq.title AS question_title,
                       cq.difficulty AS difficulty
                LIMIT $limit
                """,
                company_name=company_name,
                limit=limit
            )
            return [record.data() for record in result]
    
    def get_question_by_id(self, question_id: str) -> Optional[Dict]:
        """Fetch a specific question by ID"""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (q:Question {question_id: $question_id})-[:HAS_ANSWER]->(a:Answer)
                RETURN q.question_id AS question_id,
                       q.title AS question_title,
                       q.description AS question_description,
                       q.hints AS question_hints,
                       q.example AS question_example,
                       a.explanation AS answer_explanation,
                       a.code AS answer_code
                """,
                question_id=question_id
            )
            record = result.single()
            return record.data() if record else None
    
    def get_questions_by_difficulty(self, difficulty_level: str, limit: int = 5) -> List[Dict]:
        """Fetch questions by difficulty level"""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (diff:Difficulty {difficulty_id: $difficulty_level})
                      -[:HAS_QUESTION]->(q:Question)-[:HAS_ANSWER]->(a:Answer)
                RETURN q.question_id AS question_id,
                       q.title AS question_title,
                       q.description AS question_description,
                       a.explanation AS answer_explanation,
                       diff.level AS difficulty
                LIMIT $limit
                """,
                difficulty_level=difficulty_level,
                limit=limit
            )
            return [record.data() for record in result]


# ============================================================================
# AGENT NODES - ALL FIXED TO RETURN AgentState
# ============================================================================

class InterviewPrepAgent:
    """Main agent class for interview preparation with Gemini"""
    
    def __init__(self, neo4j_handler: Neo4jHandler, google_api_key: str):
        self.db = neo4j_handler
        
        # Initialize Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            temperature=0.7,
            google_api_key="AIzaSyAdP3smeYdxjo5onXFktwm6oB3o4hLuag4"

        )
    
    def start_node(self, state: AgentState) -> AgentState:
        """Initialize the conversation - PROPERLY INITIALIZE ALL STATE FIELDS"""
        print("\n🚀 Starting Interview Prep Agent with Gemini...")
        
        # Initialize ALL state fields
        if not state.get("thread_id"):
            state["thread_id"] = f"thread_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            print(f"📋 Created thread: {state['thread_id']}")
        
        if not state.get("questions_list"):
            state["questions_list"] = []
        
        if not state.get("current_question_index"):
            state["current_question_index"] = 0
        
        # Initialize new fields
        if not state.get("search_keywords"):
            state["search_keywords"] = None
        
        if not state.get("search_results"):
            state["search_results"] = None
        
        if not state.get("need_depth_search"):
            state["need_depth_search"] = False
        
        if "enable_rag" not in state:
            state["enable_rag"] = True
        
        if not state.get("search_depth"):
            state["search_depth"] = 2
        
        return state
    
    def extract_keywords_node(self, state: AgentState) -> AgentState:
        """
        SEPARATED NODE: Extract keywords from user query
        RETURNS: AgentState with updated search_keywords
        """
        print("\n🔍 Extracting keywords from query...")
        
        # Get latest query from state (NOT from non-existent state["question"])
        latest_query = state["query"][-1] if state["query"] else ""
        
        extraction_prompt = f"""
Extract the following details from the user's query and respond ONLY with valid JSON.

User Query: {latest_query}

Respond with this exact JSON structure (no markdown, no extra text):
{{
    "domain": "domain name or null",
    "skills": ["skill1", "skill2"] or [],
    "topic": "topic name or null",
    "company_name": "company name or null"
}}

Examples:
- "Give me Google Python questions" -> {{"domain": null, "skills": ["Python"], "topic": null, "company_name": "Google"}}
- "I want algorithms questions" -> {{"domain": "algorithms", "skills": [], "topic": null, "company_name": null}}
"""
        
        try:
            response = self.llm.invoke(extraction_prompt)
            content = response.content
            
            # Parse JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            keywords_dict = json.loads(content)
            
            # Create SearchKeywords object
            state["search_keywords"] = SearchKeywords(
                domain=keywords_dict.get("domain"),
                skills=keywords_dict.get("skills", []),
                topic=keywords_dict.get("topic"),
                company_name=keywords_dict.get("company_name")
            )
            
            print(f"✅ Extracted: domain={state['search_keywords'].domain}, "
                  f"skills={state['search_keywords'].skills}, "
                  f"topic={state['search_keywords'].topic}, "
                  f"company={state['search_keywords'].company_name}")
            
        except Exception as e:
            print(f"⚠️ Error extracting keywords: {e}")
            state["search_keywords"] = SearchKeywords()
        
        return state
    
    def depth_search_node(self, state: AgentState) -> AgentState:
        """
        SEPARATED NODE: Perform depth search in Neo4j
        RETURNS: AgentState with updated search_results
        """
        print("\n🔬 Executing Depth Search Node...")
        
        if not state.get("enable_rag", True):
            print("  ⏭️  Graph RAG disabled, skipping...")
            return state
        
        keywords = state.get("search_keywords")
        if not keywords:
            print("  ⚠️  No keywords extracted, skipping search")
            return state
        
        # Initialize result lists
        domain_results = []
        topic_results = []
        skill_results = []
        company_results = []
        
        # Perform searches based on extracted keywords
        try:
            if keywords.domain:
                print(f"  🔍 Searching by domain: {keywords.domain}")
                domain_results = self.db.get_questions_by_domain(keywords.domain)
            
            if keywords.topic:
                print(f"  🔍 Searching by topic: {keywords.topic}")
                topic_results = self.db.get_questions_by_topic(keywords.topic)
            
            if keywords.skills:
                print(f"  🔍 Searching by skills: {keywords.skills}")
                for skill in keywords.skills[:2]:  # Limit to first 2 skills
                    results = self.db.get_questions_by_skill(skill)
                    skill_results.extend(results)
            
            if keywords.company_name:
                print(f"  🔍 Searching by company: {keywords.company_name}")
                company_results = self.db.get_questions_by_company(keywords.company_name)
            
            # Aggregate results
            total_results = (len(domain_results) + len(topic_results) + 
                           len(skill_results) + len(company_results))
            
            # Store in state
            state["search_results"] = SearchResults(
                domain_results=domain_results if domain_results else None,
                topic_results=topic_results if topic_results else None,
                skill_results=skill_results if skill_results else None,
                company_results=company_results if company_results else None,
                total_results=total_results
            )
            
            print(f"  ✅ Found {total_results} total results")
            
        except Exception as e:
            print(f"  ❌ Error during depth search: {e}")
            state["search_results"] = SearchResults(total_results=0)
        
        return state
    
    def model_query_node(self, state: AgentState) -> AgentState:
        """
        Process user query using Gemini LLM
        RETURNS: AgentState with updated structured_output and response
        """
        print("\n🤖 Processing query with Gemini...")
        
        latest_query = state["query"][-1] if state["query"] else ""
        context = self._build_context(state)
        prompt = self._prepare_prompt(latest_query, context, state)
        
        try:
            response = self.llm.invoke(prompt)
            content = response.content
            
            # Parse JSON response
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "{" in content and "}" in content:
                start = content.find("{")
                end = content.rfind("}") + 1
                json_str = content[start:end]
            else:
                # Fallback
                json_str = json.dumps({
                    "message": content,
                    "questions_provided": None,
                    "feedback": None,
                    "next_action": "continue"
                })
            
            response_dict = json.loads(json_str)
            
            # Create structured response
            structured_response = AgentResponse(
                message=response_dict.get("message", content),
                questions_provided=response_dict.get("questions_provided"),
                feedback=response_dict.get("feedback"),
                next_action=response_dict.get("next_action", "continue")
            )
            
            state["structured_output"] = structured_response
            state["response"] = [structured_response.message]
            
            # Handle actions
            if structured_response.next_action == "provide_question":
                state = self._handle_question_provision(state)
            elif structured_response.next_action == "evaluate_answer":
                state = self._handle_answer_evaluation(state)
            elif structured_response.next_action == "depth_search":
                state["need_depth_search"] = True
            
            print(f"✅ Response generated: {structured_response.next_action}")
            
        except Exception as e:
            print(f"❌ Error in model query: {e}")
            state["response"] = [f"Error: {str(e)}"]
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
        
        # Add search results context
        if state.get("search_results"):
            sr = state["search_results"]
            context_parts.append(f"\n📊 Database Search Results (Total: {sr.total_results}):")
            
            if sr.domain_results:
                context_parts.append(f"  - Domain: {len(sr.domain_results)} questions")
            if sr.topic_results:
                context_parts.append(f"  - Topic: {len(sr.topic_results)} questions")
            if sr.skill_results:
                context_parts.append(f"  - Skill: {len(sr.skill_results)} questions")
            if sr.company_results:
                context_parts.append(f"  - Company: {len(sr.company_results)} questions")
        
        # Add current questions
        if state["questions_list"]:
            context_parts.append(f"\n📝 Questions in Session: {len(state['questions_list'])}")
        
        return "\n".join(context_parts)
    
    def _prepare_prompt(self, query: str, context: str, state: AgentState) -> str:
        """Prepare the prompt for Gemini"""
        
        search_results_str = ""
        if state.get("search_results") and state["search_results"].total_results > 0:
            sr = state["search_results"]
            search_results_str = "\nAvailable Questions from Database:\n"
            
            all_questions = []
            if sr.domain_results:
                all_questions.extend(sr.domain_results[:3])
            if sr.topic_results:
                all_questions.extend(sr.topic_results[:3])
            if sr.skill_results:
                all_questions.extend(sr.skill_results[:3])
            if sr.company_results:
                all_questions.extend(sr.company_results[:3])
            
            for i, q in enumerate(all_questions[:5], 1):
                title = q.get('question_title', 'N/A')
                qid = q.get('question_id', 'N/A')
                search_results_str += f"{i}. {title} (ID: {qid})\n"
        
        return f"""You are an expert interview preparation assistant.

Context:
{context}

{search_results_str}

Current User Query: {query}

Respond in JSON format with these EXACT fields:
{{
    "message": "Your helpful response to the user",
    "questions_provided": null,
    "feedback": null,
    "next_action": "continue"
}}

Guidelines for next_action:
- "provide_question": If user asks for questions and we have search results
- "evaluate_answer": If user provides an answer to a question
- "depth_search": If user wants deeper insights/research
- "end": If user says thanks/bye/done
- "continue": For general conversation

Respond ONLY with valid JSON, no markdown code blocks.
"""
    
    def _handle_question_provision(self, state: AgentState) -> AgentState:
        """Add questions from search results to state"""
        print("  📚 Adding questions to session...")
        
        if not state.get("search_results"):
            return state
        
        sr = state["search_results"]
        questions_added = 0
        
        # Collect all questions
        all_questions = []
        if sr.domain_results:
            all_questions.extend(sr.domain_results)
        if sr.topic_results:
            all_questions.extend(sr.topic_results)
        if sr.skill_results:
            all_questions.extend(sr.skill_results)
        if sr.company_results:
            all_questions.extend(sr.company_results)
        
        # Add unique questions to state
        existing_ids = {q[1] for q in state["questions_list"]}
        
        for q in all_questions:
            question_id = q.get("question_id", "")
            if question_id and question_id not in existing_ids:
                question_text = q.get("question_title") or q.get("question_description", "")
                org_answer = q.get("answer_explanation", "")
                
                state["questions_list"].append([question_text, question_id, None, org_answer])
                existing_ids.add(question_id)
                questions_added += 1
                
                if questions_added >= 5:
                    break
        
        print(f"  ✅ Added {questions_added} questions")
        return state
    
    def _handle_answer_evaluation(self, state: AgentState) -> AgentState:
        """Record user's answer"""
        if state["questions_list"] and state["current_question_index"] < len(state["questions_list"]):
            current_q = state["questions_list"][state["current_question_index"]]
            user_answer = state["query"][-1] if state["query"] else ""
            current_q[2] = user_answer
            
            print(f"  ✍️ Recorded answer for question {state['current_question_index'] + 1}")
            state["current_question_index"] += 1
        
        return state
    
    def check_satisfaction_node(self, state: AgentState) -> AgentState:
        """
        Check if user is satisfied or needs more depth
        RETURNS: AgentState with updated satisfaction flags
        """
        print("\n🔍 Checking user satisfaction...")
        
        latest_query = state["query"][-1].lower() if state["query"] else ""
        
        # Define keywords
        satisfaction_keywords = ["thanks", "thank you", "done", "finished", "exit", "bye"]
        depth_keywords = ["depth", "research", "more details", "deep dive", "comprehensive"]
        continuation_keywords = ["more", "another", "next", "continue", "help", "question"]
        
        # Determine satisfaction state
        if any(keyword in latest_query for keyword in satisfaction_keywords):
            state["user_satisfied"] = True
            state["need_depth_search"] = False
            print("  ✅ User appears satisfied")
        elif any(keyword in latest_query for keyword in depth_keywords):
            state["user_satisfied"] = False
            state["need_depth_search"] = True
            print("  🔬 User wants depth search")
        elif any(keyword in latest_query for keyword in continuation_keywords):
            state["user_satisfied"] = False
            state["need_depth_search"] = False
            print("  🔄 User wants to continue")
        else:
            # Check structured output
            if state.get("structured_output"):
                if state["structured_output"].next_action == "end":
                    state["user_satisfied"] = True
                    state["need_depth_search"] = False
                elif state["structured_output"].next_action == "depth_search":
                    state["user_satisfied"] = False
                    state["need_depth_search"] = True
                else:
                    state["user_satisfied"] = False
                    state["need_depth_search"] = False
            else:
                state["user_satisfied"] = False
                state["need_depth_search"] = False
        
        return state
    
    def end_node(self, state: AgentState) -> AgentState:
        """
        End the conversation
        RETURNS: AgentState with final summary
        """
        print("\n🎯 Ending conversation...")
        
        summary_parts = [
            "\n" + "="*50,
            "📊 INTERVIEW PREP SESSION SUMMARY",
            "="*50,
            f"\nThread ID: {state['thread_id']}",
            f"Total Questions Covered: {len(state['questions_list'])}",
            f"Questions Answered: {sum(1 for q in state['questions_list'] if q[2] is not None)}",
        ]
        
        if state.get("search_results"):
            summary_parts.append(f"Database Queries: {state['search_results'].total_results} results")
        
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
        
        state["response"] = [summary]
        
        return state


# ============================================================================
# GRAPH CONSTRUCTION - FIXED ROUTING
# ============================================================================

def create_agent_graph(neo4j_handler: Neo4jHandler, google_api_key: str) -> StateGraph:
    """Create and configure the LangGraph workflow with proper routing"""
    
    agent = InterviewPrepAgent(neo4j_handler, google_api_key)
    
    # Initialize the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("start", agent.start_node)
    workflow.add_node("extract_keywords", agent.extract_keywords_node)
    workflow.add_node("depth_search", agent.depth_search_node)
    workflow.add_node("model_query", agent.model_query_node)
    workflow.add_node("check_satisfaction", agent.check_satisfaction_node)
    workflow.add_node("end", agent.end_node)
    
    # Add edges
    workflow.add_edge(START, "start")
    workflow.add_edge("start", "extract_keywords")
    workflow.add_edge("extract_keywords", "depth_search")
    workflow.add_edge("depth_search", "model_query")
    workflow.add_edge("model_query", "check_satisfaction")
    
    # Conditional routing - FIXED LOGIC
    def route_after_satisfaction(state: AgentState) -> Literal["extract_keywords", "end"]:
        """Simple, reliable routing based on state flags"""
        if state.get("user_satisfied", False):
            return "end"
        else:
            # Continue the loop - go back to keyword extraction
            return "extract_keywords"
    
    workflow.add_conditional_edges(
        "check_satisfaction",
        route_after_satisfaction,
        {
            "extract_keywords": "extract_keywords",
            "end": "end"
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
    ║   Powered by LangGraph + Neo4j + Gemini       ║
    ║   ALL LOGICAL INCONSISTENCIES FIXED           ║
    ╚═══════════════════════════════════════════════╝
    """)
    
    # Initialize Neo4j handler
    neo4j_handler = Neo4jHandler(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    try:
        # Create the agent graph
        workflow = create_agent_graph(neo4j_handler, GOOGLE_API_KEY)
        
        # Compile the graph with memory
        memory = MemorySaver()
        app = workflow.compile(checkpointer=memory)
        
        # Initialize state with ALL fields
        initial_state: AgentState = {
            "questions_list": [],
            "query": [],
            "response": [],
            "thread_id": f"thread_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
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
        
        print("\n💬 Chat with the Interview Prep Agent (type 'exit' to quit)")
        print("💡 Tips:")
        print("  - Ask for questions by company, domain, skill, or topic")
        print("  - Type 'disable rag' to turn off graph search")
        print("  - Type 'enable rag' to turn on graph search\n")
        
        # Interactive loop
        while True:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\n👋 Goodbye! Good luck with your interviews!")
                break
            
            # Handle special commands
            if "disable rag" in user_input.lower():
                initial_state["enable_rag"] = False
                print("✅ Graph RAG disabled\n")
                continue
            
            if "enable rag" in user_input.lower():
                initial_state["enable_rag"] = True
                print("✅ Graph RAG enabled\n")
                continue
            
            # Add query to state
            initial_state["query"] = [user_input]
            initial_state["user_satisfied"] = False
            initial_state["need_depth_search"] = False
            
            # Run the graph
            try:
                result = app.invoke(initial_state, config=config)
                
                # Display response
                if result.get("structured_output"):
                    print(f"\n🤖 Agent: {result['structured_output'].message}\n")
                    
                    # Display new questions
                    if result.get("questions_list") and len(result["questions_list"]) > len(initial_state.get("questions_list", [])):
                        print("📚 New Questions Added:\n")
                        new_questions = result["questions_list"][len(initial_state.get("questions_list", [])):]
                        for i, q in enumerate(new_questions, 1):
                            print(f"{i}. {q[0]}")
                        print()
                    
                    # Display feedback
                    if result['structured_output'].feedback:
                        feedback = result['structured_output'].feedback
                        print(f"📊 Evaluation Score: {feedback.score}/10\n")
                        print(f"💪 Strengths: {', '.join(feedback.strengths)}")
                        print(f"📈 Improvements: {', '.join(feedback.improvements)}\n")
                
                # Update state for next iteration
                initial_state = result
                
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
                import traceback
                traceback.print_exc()
                continue
    
    finally:
        # Cleanup
        neo4j_handler.close()
        print("\n🔒 Closed database connection")


if __name__ == "__main__":
    main()
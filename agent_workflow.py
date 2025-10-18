from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Annotated
import operator
from vertexai.generative_models import GenerativeModel
import vertexai
import json

# Initialize Vertex AI
vertexai.init(project=os.getenv('GOOGLE_CLOUD_PROJECT'), location=os.getenv('GOOGLE_CLOUD_REGION'))

class AgentState(TypedDict):
    """State passed between agents"""
    # Input
    incident_description: str
    
    # Analysis phase
    incident_analysis: Dict
    severity: str
    incident_type: str
    technical_terms: List[str]
    affected_systems: List[str]
    
    # Search phase
    search_strategy: Dict
    search_results: Annotated[List[Dict], operator.add]  # Accumulate results
    
    # Synthesis phase
    resolution_recommendation: Dict
    confidence_score: float
    explanation: str
    
    # Metadata
    processing_time: float
    agent_steps: Annotated[List[str], operator.add]


class DevOpsOracleAgent:
    def __init__(self, search_engine):
        self.model = GenerativeModel("gemini-2.0-flash-exp")
        self.embedding_model = GenerativeModel("text-embedding-004")
        self.search_engine = search_engine
    
    def analyze_incident(self, state: AgentState) -> AgentState:
        """Analyzer Agent: Extract key information from incident description"""
        print("🔍 Analyzer Agent: Analyzing incident...")
        
        prompt = f"""
        You are an expert DevOps engineer analyzing a production incident.
        
        Incident Description:
        {state['incident_description']}
        
        Extract and return ONLY a JSON object with these fields:
        {{
            "severity": "P0|P1|P2|P3",
            "incident_type": "database|network|application|infrastructure|security",
            "key_symptoms": ["symptom1", "symptom2"],
            "technical_terms": ["term1", "term2"],
            "affected_systems": ["system1", "system2"],
            "urgency_score": 1-10,
            "summary": "one-sentence technical summary"
        }}
        
        Be precise and technical. Extract actual error messages and technical terms.
        """
        
        response = self.model.generate_content(prompt)
        analysis = json.loads(response.text)
        
        return {
            **state,
            "incident_analysis": analysis,
            "severity": analysis["severity"],
            "incident_type": analysis["incident_type"],
            "technical_terms": analysis["technical_terms"],
            "affected_systems": analysis["affected_systems"],
            "agent_steps": ["analyze_incident"]
        }
    
    def create_search_strategy(self, state: AgentState) -> AgentState:
        """Strategy Agent: Determine how to search for solutions"""
        print("🎯 Strategy Agent: Planning search approach...")
        
        prompt = f"""
        Based on this incident analysis, determine the search strategy.
        
        Analysis:
        {json.dumps(state['incident_analysis'], indent=2)}
        
        Return ONLY a JSON object:
        {{
            "primary_search_terms": ["term1", "term2"],
            "secondary_search_terms": ["term3", "term4"],
            "source_priorities": ["logs", "past_incidents", "documentation"],
            "filters": {{"incident_type": "database", "severity": "P1"}},
            "expected_resolution_patterns": ["pattern1", "pattern2"]
        }}
        """
        
        response = self.model.generate_content(prompt)
        strategy = json.loads(response.text)
        
        return {
            **state,
            "search_strategy": strategy,
            "agent_steps": ["create_search_strategy"]
        }
    
    def execute_search(self, state: AgentState) -> AgentState:
        """Search Agent: Execute hybrid searches across knowledge sources"""
        print("🔎 Search Agent: Executing hybrid search...")
        
        # Generate embedding for semantic search
        embedding_response = self.embedding_model.generate_content(
            state['incident_description']
        )
        query_vector = embedding_response.embeddings[0].values
        
        # Combine technical terms for keyword search
        search_text = " ".join(
            state['search_strategy']['primary_search_terms'] +
            state['technical_terms']
        )
        
        # Execute hybrid search
        results = self.search_engine.hybrid_search(
            query_text=search_text,
            query_vector=query_vector,
            filters=state['search_strategy'].get('filters'),
            size=10,
            keyword_boost=1.0,
            vector_boost=2.0
        )
        
        return {
            **state,
            "search_results": results,
            "agent_steps": ["execute_search"]
        }
    
    def synthesize_resolution(self, state: AgentState) -> AgentState:
        """Synthesis Agent: Generate actionable resolution recommendation"""
        print("🎓 Synthesis Agent: Generating resolution strategy...")
        
        # Prepare context from search results
        top_results = state['search_results'][:5]
        results_context = "\n\n".join([
            f"Result {i+1} (Score: {r['score']:.2f}):\n"
            f"Title: {r['title']}\n"
            f"Type: {r['incident_type']}, Severity: {r['severity']}\n"
            f"Resolution: {r['resolution_steps']}\n"
            f"Time to resolve: {r['resolution_time_minutes']} minutes"
            for i, r in enumerate(top_results)
        ])
        
        prompt = f"""
        You are an expert DevOps engineer providing incident resolution guidance.
        
        Current Incident:
        {state['incident_description']}
        
        Analysis:
        {json.dumps(state['incident_analysis'], indent=2)}
        
        Similar Past Incidents:
        {results_context}
        
        Provide a resolution recommendation as JSON:
        {{
            "immediate_actions": ["step1", "step2", "step3"],
            "root_cause_hypothesis": "detailed explanation",
            "resolution_steps": ["detailed step 1", "detailed step 2"],
            "preventive_measures": ["measure1", "measure2"],
            "estimated_resolution_time_minutes": 15,
            "confidence_score": 0.85,
            "confidence_reasoning": "why this confidence level",
            "similar_incident_references": ["incident_id1", "incident_id2"],
            "risk_assessment": "low|medium|high"
        }}
        
        Be specific and actionable. Reference the similar incidents.
        """
        
        response = self.model.generate_content(prompt)
        recommendation = json.loads(response.text)
        
        return {
            **state,
            "resolution_recommendation": recommendation,
            "confidence_score": recommendation["confidence_score"],
            "explanation": recommendation["confidence_reasoning"],
            "agent_steps": ["synthesize_resolution"]
        }


def create_workflow(search_engine) -> StateGraph:
    """Create the LangGraph workflow"""
    agent = DevOpsOracleAgent(search_engine)
    
    # Create graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("analyze", agent.analyze_incident)
    workflow.add_node("strategize", agent.create_search_strategy)
    workflow.add_node("search", agent.execute_search)
    workflow.add_node("synthesize", agent.synthesize_resolution)
    
    # Define edges (linear flow for now)
    workflow.add_edge("analyze", "strategize")
    workflow.add_edge("strategize", "search")
    workflow.add_edge("search", "synthesize")
    workflow.add_edge("synthesize", END)
    
    # Set entry point
    workflow.set_entry_point("analyze")
    
    return workflow.compile()
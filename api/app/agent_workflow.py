from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Annotated
import operator
from vertexai.generative_models import GenerativeModel
import vertexai
import json
import logging
import time

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """State passed between agents"""
    # Input
    incident_description: str
    request_id: str
    
    # Analysis phase
    incident_analysis: Dict
    
    # Search phase
    search_results: List[Dict]
    
    # Synthesis phase
    resolution_recommendation: Dict
    
    # Metadata
    processing_time: float
    agent_steps: Annotated[List[str], operator.add]
    errors: Annotated[List[str], operator.add]

class DevOpsOracleAgent:
    def __init__(self, search_engine, project_id: str, region: str):
        vertexai.init(project=project_id, location=region)
        self.model = GenerativeModel("deepseek-r1-0528-maas")
        self.embedding_model = GenerativeModel("text-embedding-004")
        self.search_engine = search_engine
        
    def analyze_incident(self, state: AgentState) -> AgentState:
        """Analyzer Agent: Extract key information from incident description"""
        logger.info(f"🔍 Analyzer Agent: Processing incident {state['request_id']}")
        start_time = time.time()
        
        try:
            prompt = f"""
You are an expert DevOps engineer analyzing a production incident.

Incident Description:
{state['incident_description']}

Extract and return ONLY a valid JSON object with these exact fields:
{{
    "severity": "P0 or P1 or P2 or P3",
    "incident_type": "database or network or application or infrastructure or security",
    "key_symptoms": ["symptom1", "symptom2"],
    "technical_terms": ["term1", "term2"],
    "affected_systems": ["system1", "system2"],
    "urgency_score": 8,
    "summary": "one-sentence technical summary"
}}

Rules:
- severity must be exactly one of: P0, P1, P2, P3
- incident_type must be exactly one of: database, network, application, infrastructure, security
- urgency_score must be an integer between 1-10
- Extract actual technical terms, error codes, and system names
- Be precise and technical

Return ONLY the JSON object, no other text.
"""
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean up response (remove markdown if present)
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            elif response_text.startswith("```"):
                response_text = response_text.replace("```", "").strip()
            
            analysis = json.loads(response_text)
            
            elapsed = time.time() - start_time
            logger.info(f"✅ Analysis complete in {elapsed:.2f}s: {analysis['severity']} {analysis['incident_type']}")
            
            return {
                **state,
                "incident_analysis": analysis,
                "agent_steps": [f"analyze_incident ({elapsed:.2f}s)"],
                "errors": []
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse analysis JSON: {e}")
            logger.error(f"Response was: {response_text}")
            # Provide fallback analysis
            return {
                **state,
                "incident_analysis": {
                    "severity": "P2",
                    "incident_type": "application",
                    "key_symptoms": ["error detected"],
                    "technical_terms": [],
                    "affected_systems": ["unknown"],
                    "urgency_score": 5,
                    "summary": "Unable to fully analyze incident"
                },
                "agent_steps": ["analyze_incident (failed, using fallback)"],
                "errors": [f"Analysis parsing error: {str(e)}"]
            }
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            raise
    
    def create_search_strategy(self, state: AgentState) -> AgentState:
        """Strategy Agent: Determine how to search for solutions"""
        logger.info(f"🎯 Strategy Agent: Planning search for {state['request_id']}")
        start_time = time.time()
        
        try:
            analysis = state['incident_analysis']
            
            prompt = f"""
Based on this incident analysis, determine the optimal search strategy.

Analysis:
{json.dumps(analysis, indent=2)}

Return ONLY a valid JSON object:
{{
    "primary_search_terms": ["term1", "term2", "term3"],
    "search_filters": {{"incident_type": "database"}},
    "search_priority": "past_incidents or documentation or logs"
}}

Focus on:
- Technical terms that will find similar incidents
- Error codes, exception names, system components
- Root cause indicators

Return ONLY the JSON object, no other text.
"""
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean up response
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            elif response_text.startswith("```"):
                response_text = response_text.replace("```", "").strip()
            
            strategy = json.loads(response_text)
            
            elapsed = time.time() - start_time
            logger.info(f"✅ Strategy created in {elapsed:.2f}s")
            
            return {
                **state,
                "search_strategy": strategy,
                "agent_steps": [f"create_search_strategy ({elapsed:.2f}s)"]
            }
            
        except Exception as e:
            logger.error(f"Strategy error: {e}")
            # Fallback strategy
            return {
                **state,
                "search_strategy": {
                    "primary_search_terms": state['incident_analysis'].get('technical_terms', []),
                    "search_filters": {"incident_type": state['incident_analysis']['incident_type']},
                    "search_priority": "past_incidents"
                },
                "agent_steps": ["create_search_strategy (fallback)"],
                "errors": [f"Strategy error: {str(e)}"]
            }
    
    def execute_search(self, state: AgentState) -> AgentState:
        """Search Agent: Execute hybrid search"""
        logger.info(f"🔎 Search Agent: Executing search for {state['request_id']}")
        start_time = time.time()
        
        try:
            # Generate embedding for semantic search
            embedding_text = state['incident_description']
            embedding_response = self.embedding_model.generate_content(embedding_text)
            query_vector = embedding_response.embeddings[0].values
            
            # Prepare search query
            strategy = state.get('search_strategy', {})
            search_terms = strategy.get('primary_search_terms', [])
            search_text = " ".join(search_terms + state['incident_analysis'].get('technical_terms', []))
            
            filters = strategy.get('search_filters', {})
            
            # Execute hybrid search
            results = self.search_engine.hybrid_search(
                query_text=search_text,
                query_vector=query_vector,
                filters=filters,
                size=10,
                keyword_boost=1.0,
                vector_boost=2.0
            )
            
            elapsed = time.time() - start_time
            logger.info(f"✅ Search complete in {elapsed:.2f}s: {len(results)} results")
            
            return {
                **state,
                "search_results": results,
                "agent_steps": [f"execute_search ({elapsed:.2f}s, {len(results)} results)"]
            }
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return {
                **state,
                "search_results": [],
                "agent_steps": ["execute_search (failed)"],
                "errors": [f"Search error: {str(e)}"]
            }
    
    def synthesize_resolution(self, state: AgentState) -> AgentState:
        """Synthesis Agent: Generate actionable resolution recommendation"""
        logger.info(f"🎓 Synthesis Agent: Generating resolution for {state['request_id']}")
        start_time = time.time()
        
        try:
            # Prepare context from top search results
            top_results = state['search_results'][:5]
            
            if not top_results:
                results_context = "No similar incidents found in database."
            else:
                results_context = "\n\n".join([
                    f"Similar Incident {i+1} (Similarity: {r['similarity_score']:.2f}):\n"
                    f"ID: {r['incident_id']}\n"
                    f"Title: {r['title']}\n"
                    f"Type: {r['incident_type']}, Severity: {r['severity']}\n"
                    f"Resolution: {r['resolution_steps'][:300]}...\n"
                    f"Time to resolve: {r['resolution_time_minutes']} minutes"
                    for i, r in enumerate(top_results)
                ])
            
            prompt = f"""
You are an expert DevOps engineer providing incident resolution guidance.

Current Incident:
{state['incident_description']}

Incident Analysis:
{json.dumps(state['incident_analysis'], indent=2)}

Similar Past Incidents:
{results_context}

Provide a comprehensive resolution recommendation as JSON:
{{
    "immediate_actions": ["specific action 1", "specific action 2", "specific action 3"],
    "root_cause_hypothesis": "detailed technical explanation of likely root cause",
    "resolution_steps": ["detailed step 1 with commands", "detailed step 2 with commands", "step 3"],
    "preventive_measures": ["prevention 1", "prevention 2"],
    "estimated_resolution_time_minutes": 20,
    "confidence_score": 0.85,
    "confidence_reasoning": "explain why this confidence level based on similarity and past incidents",
    "similar_incident_references": ["INC-10001", "INC-10002"],
    "risk_assessment": "low or medium or high"
}}

Requirements:
- Be specific and actionable (include actual commands, configs, etc)
- confidence_score must be between 0 and 1
- Base confidence on similarity scores from search results
- Reference the similar incident IDs if found
- estimated_resolution_time_minutes should be realistic
- If no similar incidents found, base on incident analysis and lower confidence

Return ONLY the JSON object, no other text.
"""
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean up response
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            elif response_text.startswith("```"):
                response_text = response_text.replace("```", "").strip()
            
            recommendation = json.loads(response_text)
            
            elapsed = time.time() - start_time
            logger.info(f"✅ Resolution synthesized in {elapsed:.2f}s (confidence: {recommendation['confidence_score']:.2f})")
            
            return {
                **state,
                "resolution_recommendation": recommendation,
                "agent_steps": [f"synthesize_resolution ({elapsed:.2f}s)"]
            }
            
        except Exception as e:
            logger.error(f"Synthesis error: {e}")
            # Provide fallback recommendation
            return {
                **state,
                "resolution_recommendation": {
                    "immediate_actions": ["Check system logs", "Verify service health", "Review recent deployments"],
                    "root_cause_hypothesis": "Unable to determine specific root cause without similar incidents",
                    "resolution_steps": ["Investigate logs", "Check monitoring", "Escalate if needed"],
                    "preventive_measures": ["Add monitoring", "Review logs regularly"],
                    "estimated_resolution_time_minutes": 30,
                    "confidence_score": 0.3,
                    "confidence_reasoning": "Low confidence due to synthesis error or no similar incidents",
                    "similar_incident_references": [],
                    "risk_assessment": "medium"
                },
                "agent_steps": ["synthesize_resolution (fallback)"],
                "errors": [f"Synthesis error: {str(e)}"]
            }

def create_workflow(search_engine, project_id: str, region: str) -> StateGraph:
    """Create the LangGraph workflow"""
    agent = DevOpsOracleAgent(search_engine, project_id, region)
    
    # Create graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("analyze", agent.analyze_incident)
    workflow.add_node("strategize", agent.create_search_strategy)
    workflow.add_node("search", agent.execute_search)
    workflow.add_node("synthesize", agent.synthesize_resolution)
    
    # Define edges (linear flow)
    workflow.add_edge("analyze", "strategize")
    workflow.add_edge("strategize", "search")
    workflow.add_edge("search", "synthesize")
    workflow.add_edge("synthesize", END)
    
    # Set entry point
    workflow.set_entry_point("analyze")
    
    return workflow.compile()
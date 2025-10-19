from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import logging
import uuid
from datetime import datetime
import time
import json
from contextlib import asynccontextmanager

from app.config import get_settings
from app.models import (
    IncidentRequest, IncidentResponse, HealthResponse, ErrorResponse,
    IncidentAnalysis, SearchResult, ResolutionRecommendation
)
from app.search_engine import HybridSearchEngine
from app.agent_workflow import create_workflow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables for dependencies
search_engine = None
agent_workflow = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global search_engine, agent_workflow
    
    settings = get_settings()
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Initialize Elasticsearch
    try:
        search_engine = HybridSearchEngine(
            cloud_id=settings.ELASTIC_CLOUD_ID,
            api_key=settings.ELASTIC_API_KEY,
            index_name=settings.ELASTIC_INDEX_NAME
        )
        logger.info("✅ Elasticsearch initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Elasticsearch: {e}")
        raise
    
    # Initialize agent workflow
    try:
        agent_workflow = create_workflow(
            search_engine=search_engine,
            project_id=settings.GOOGLE_CLOUD_PROJECT,
            region=settings.GOOGLE_CLOUD_REGION
        )
        logger.info("✅ Agent workflow initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize agent workflow: {e}")
        raise
    
    yield
    
    # Cleanup
    logger.info("👋 Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="DevOps Oracle API",
    description="AI-Powered Incident Resolution System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_model=dict)
async def root():
    """Root endpoint"""
    return {
        "service": "DevOps Oracle API",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check Elasticsearch
        es_stats = search_engine.get_index_stats()
        es_status = es_stats.get('status', 'unknown')
        
        return HealthResponse(
            status="healthy" if es_status == "healthy" else "degraded",
            version=settings.APP_VERSION,
            timestamp=datetime.now(),
            services={
                "elasticsearch": es_status,
                "agent_workflow": "healthy" if agent_workflow else "unhealthy",
                "vertex_ai": "healthy"
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.post("/api/v1/incidents/analyze", response_model=IncidentResponse)
async def analyze_incident(request: IncidentRequest):
    """
    Analyze an incident and provide resolution recommendations
    
    This endpoint orchestrates the multi-agent workflow:
    1. Analyze incident to extract key information
    2. Create search strategy
    3. Execute hybrid search across knowledge base
    4. Synthesize resolution recommendation
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    logger.info(f"📨 Received incident analysis request {request_id}")
    logger.info(f"Description: {request.description[:100]}...")
    
    try:
        # Execute agent workflow
        initial_state = {
            "incident_description": request.description,
            "request_id": request_id,
            "agent_steps": [],
            "errors": []
        }
        
        result = agent_workflow.invoke(initial_state)
        
        processing_time = time.time() - start_time
        
        # Build response
        response = IncidentResponse(
            request_id=request_id,
            timestamp=datetime.now(),
            incident_description=request.description,
            analysis=IncidentAnalysis(**result['incident_analysis']),
            search_results=[SearchResult(**r) for r in result['search_results']],
            recommendation=ResolutionRecommendation(**result['resolution_recommendation']),
            processing_time_seconds=round(processing_time, 2),
            agent_steps=result['agent_steps']
        )
        
        logger.info(f"✅ Request {request_id} completed in {processing_time:.2f}s")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Error processing request {request_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process incident: {str(e)}"
        )

@app.post("/api/v1/incidents/analyze/stream")
async def analyze_incident_stream(request: IncidentRequest):
    """
    Stream incident analysis results in real-time
    
    Returns Server-Sent Events (SSE) for real-time updates during analysis
    """
    request_id = str(uuid.uuid4())
    
    async def event_generator():
        try:
            yield f"data: {json.dumps({'type': 'start', 'request_id': request_id})}\n\n"
            
            # Execute workflow with streaming updates
            initial_state = {
                "incident_description": request.description,
                "request_id": request_id,
                "agent_steps": [],
                "errors": []
            }
            
            # For streaming, we'll execute and send updates at each step
            # Note: This is a simplified version. For true streaming, you'd need to modify the workflow
            
            yield f"data: {json.dumps({'type': 'step', 'step': 'Analyzing incident...'})}\n\n"
            
            result = agent_workflow.invoke(initial_state)
            
            # Send analysis
            yield f"data: {json.dumps({'type': 'analysis', 'data': result['incident_analysis']})}\n\n"
            
            # Send search results
            yield f"data: {json.dumps({'type': 'search_results', 'data': result['search_results']})}\n\n"
            
            # Send recommendation
            yield f"data: {json.dumps({'type': 'recommendation', 'data': result['resolution_recommendation']})}\n\n"
            
            # Send complete
            yield f"data: {json.dumps({'type': 'complete', 'agent_steps': result['agent_steps']})}\n\n"
            
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.get("/api/v1/incidents/{incident_id}")
async def get_incident(incident_id: str):
    """Retrieve a specific incident by ID"""
    try:
        incident = search_engine.get_incident_by_id(incident_id)
        if not incident:
            raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
        return incident
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving incident: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/stats")
async def get_stats():
    """Get system statistics"""
    try:
        stats = search_engine.get_index_stats()
        return {
            "elasticsearch": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return ErrorResponse(
        error="Internal Server Error",
        detail=str(exc),
        timestamp=datetime.now()
    )

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
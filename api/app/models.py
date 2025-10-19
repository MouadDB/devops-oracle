from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class SeverityLevel(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"

class IncidentType(str, Enum):
    DATABASE = "database"
    NETWORK = "network"
    APPLICATION = "application"
    INFRASTRUCTURE = "infrastructure"
    SECURITY = "security"

class IncidentRequest(BaseModel):
    description: str = Field(..., min_length=10, description="Detailed incident description")
    user_id: Optional[str] = Field(None, description="User ID for tracking")
    
    class Config:
        json_schema_extra = {
            "example": {
                "description": "Users reporting 500 errors on checkout. Error logs show: HikariCP - Connection is not available, request timed out after 30000ms. Connection pool exhausted.",
                "user_id": "user_123"
            }
        }

class IncidentAnalysis(BaseModel):
    severity: SeverityLevel
    incident_type: IncidentType
    key_symptoms: List[str]
    technical_terms: List[str]
    affected_systems: List[str]
    urgency_score: int = Field(..., ge=1, le=10)
    summary: str

class SearchResult(BaseModel):
    incident_id: str
    title: str
    description: str
    severity: str
    incident_type: str
    resolution_steps: str
    resolution_time_minutes: int
    similarity_score: float
    created_at: str
    highlights: Dict[str, List[str]] = {}

class ResolutionRecommendation(BaseModel):
    immediate_actions: List[str]
    root_cause_hypothesis: str
    resolution_steps: List[str]
    preventive_measures: List[str]
    estimated_resolution_time_minutes: int
    confidence_score: float = Field(..., ge=0, le=1)
    confidence_reasoning: str
    similar_incident_references: List[str]
    risk_assessment: str

class IncidentResponse(BaseModel):
    request_id: str
    timestamp: datetime
    incident_description: str
    analysis: IncidentAnalysis
    search_results: List[SearchResult]
    recommendation: ResolutionRecommendation
    processing_time_seconds: float
    agent_steps: List[str]

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime
    services: Dict[str, str]

class ErrorResponse(BaseModel):
    error: str
    detail: str
    timestamp: datetime
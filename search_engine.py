from elasticsearch import Elasticsearch
from typing import List, Dict
import os

class HybridSearchEngine:
    def __init__(self):
        self.es = Elasticsearch(
            cloud_id=os.getenv('ELASTIC_CLOUD_ID'),
            api_key=os.getenv('ELASTIC_API_KEY')
        )
        self.index_name = os.getenv('ELASTIC_INDEX_NAME', 'devops-incidents')
    
    def hybrid_search(
        self,
        query_text: str,
        query_vector: List[float],
        filters: Dict = None,
        size: int = 10,
        keyword_boost: float = 1.0,
        vector_boost: float = 2.0
    ) -> List[Dict]:
        """
        Perform hybrid search combining keyword (BM25) and vector (semantic) search
        
        Args:
            query_text: Text query for keyword search
            query_vector: Embedding vector for semantic search
            filters: Optional filters (severity, incident_type, etc.)
            size: Number of results to return
            keyword_boost: Boost factor for keyword search
            vector_boost: Boost factor for vector search
        """
        
        # Build the hybrid query
        must_clauses = []
        should_clauses = []
        
        # Keyword search (BM25)
        should_clauses.append({
            "multi_match": {
                "query": query_text,
                "fields": [
                    "title^3",  # Title is most important
                    "description^2",
                    "error_messages^2",
                    "resolution_steps",
                    "root_cause"
                ],
                "type": "best_fields",
                "boost": keyword_boost
            }
        })
        
        # Vector search (semantic)
        should_clauses.append({
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'description_embedding') + 1.0",
                    "params": {"query_vector": query_vector}
                },
                "boost": vector_boost
            }
        })
        
        # Add filters if provided
        if filters:
            for field, value in filters.items():
                if isinstance(value, list):
                    must_clauses.append({"terms": {field: value}})
                else:
                    must_clauses.append({"term": {field: value}})
        
        # Construct final query
        query = {
            "size": size,
            "query": {
                "bool": {
                    "must": must_clauses if must_clauses else [{"match_all": {}}],
                    "should": should_clauses,
                    "minimum_should_match": 1
                }
            },
            "highlight": {
                "fields": {
                    "description": {},
                    "error_messages": {},
                    "resolution_steps": {}
                },
                "pre_tags": ["<mark>"],
                "post_tags": ["</mark>"]
            }
        }
        
        # Execute search
        response = self.es.search(index=self.index_name, body=query)
        
        # Format results
        results = []
        for hit in response['hits']['hits']:
            result = {
                'score': hit['_score'],
                'incident_id': hit['_source'].get('incident_id'),
                'title': hit['_source'].get('title'),
                'description': hit['_source'].get('description'),
                'severity': hit['_source'].get('severity'),
                'incident_type': hit['_source'].get('incident_type'),
                'resolution_steps': hit['_source'].get('resolution_steps'),
                'resolution_time_minutes': hit['_source'].get('resolution_time_minutes'),
                'created_at': hit['_source'].get('created_at'),
                'highlights': hit.get('highlight', {})
            }
            results.append(result)
        
        return results
    
    def search_by_type(self, incident_type: str, query_vector: List[float], size: int = 5):
        """Search for similar incidents of a specific type"""
        return self.hybrid_search(
            query_text="",
            query_vector=query_vector,
            filters={"incident_type": incident_type},
            size=size,
            keyword_boost=0.5,
            vector_boost=2.0
        )
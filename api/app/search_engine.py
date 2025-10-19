from elasticsearch import Elasticsearch
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class HybridSearchEngine:
    def __init__(self, cloud_id: str, api_key: str, index_name: str):
        self.es = Elasticsearch(
            cloud_id=cloud_id,
            api_key=api_key
        )
        self.index_name = index_name
        self._verify_connection()
    
    def _verify_connection(self):
        """Verify Elasticsearch connection"""
        try:
            if not self.es.ping():
                raise ConnectionError("Cannot connect to Elasticsearch")
            logger.info(f"✅ Connected to Elasticsearch cluster")
        except Exception as e:
            logger.error(f"❌ Elasticsearch connection failed: {e}")
            raise
    
    def hybrid_search(
        self,
        query_text: str,
        query_vector: List[float],
        filters: Optional[Dict] = None,
        size: int = 10,
        keyword_boost: float = 1.0,
        vector_boost: float = 2.0
    ) -> List[Dict]:
        """
        Perform hybrid search combining keyword (BM25) and vector (semantic) search
        """
        try:
            # Build should clauses for hybrid search
            should_clauses = []
            
            # Keyword search (BM25)
            if query_text:
                should_clauses.append({
                    "multi_match": {
                        "query": query_text,
                        "fields": [
                            "title^3",
                            "description^2",
                            "error_messages^2",
                            "resolution_steps",
                            "root_cause",
                            "technical_terms^2"
                        ],
                        "type": "best_fields",
                        "boost": keyword_boost,
                        "fuzziness": "AUTO"
                    }
                })
            
            # Vector search (semantic similarity)
            if query_vector:
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
            
            # Build filter clauses
            filter_clauses = []
            if filters:
                for field, value in filters.items():
                    if isinstance(value, list):
                        filter_clauses.append({"terms": {field: value}})
                    else:
                        filter_clauses.append({"term": {field: value}})
            
            # Construct query
            query = {
                "size": size,
                "query": {
                    "bool": {
                        "should": should_clauses,
                        "filter": filter_clauses,
                        "minimum_should_match": 1
                    }
                },
                "highlight": {
                    "fields": {
                        "description": {"fragment_size": 150, "number_of_fragments": 3},
                        "error_messages": {"fragment_size": 150, "number_of_fragments": 2},
                        "resolution_steps": {"fragment_size": 200, "number_of_fragments": 3}
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
                source = hit['_source']
                result = {
                    'incident_id': source.get('incident_id'),
                    'title': source.get('title'),
                    'description': source.get('description'),
                    'severity': source.get('severity'),
                    'incident_type': source.get('incident_type'),
                    'resolution_steps': source.get('resolution_steps'),
                    'resolution_time_minutes': source.get('resolution_time_minutes', 0),
                    'created_at': source.get('created_at'),
                    'similarity_score': hit['_score'],
                    'highlights': hit.get('highlight', {})
                }
                results.append(result)
            
            logger.info(f"Found {len(results)} results for query")
            return results
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            raise
    
    def get_incident_by_id(self, incident_id: str) -> Optional[Dict]:
        """Retrieve a specific incident by ID"""
        try:
            response = self.es.get(index=self.index_name, id=incident_id)
            return response['_source']
        except Exception as e:
            logger.warning(f"Incident {incident_id} not found: {e}")
            return None
    
    def get_index_stats(self) -> Dict:
        """Get statistics about the index"""
        try:
            count = self.es.count(index=self.index_name)
            stats = self.es.indices.stats(index=self.index_name)
            
            return {
                "document_count": count['count'],
                "index_size_bytes": stats['indices'][self.index_name]['total']['store']['size_in_bytes'],
                "status": "healthy"
            }
        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            return {"status": "error", "error": str(e)}
from elasticsearch import Elasticsearch
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to Elasticsearch
es = Elasticsearch(
    cloud_id=os.getenv('ELASTIC_CLOUD_ID'),
    api_key=os.getenv('ELASTIC_API_KEY')
)

# Index name
INDEX_NAME = "devops-incidents"

# Index mapping with hybrid search support
INDEX_MAPPING = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 1,
        "analysis": {
            "analyzer": {
                "technical_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "stop", "porter_stem"]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            # Core incident fields
            "incident_id": {"type": "keyword"},
            "title": {
                "type": "text",
                "analyzer": "technical_analyzer",
                "fields": {
                    "keyword": {"type": "keyword"}
                }
            },
            "description": {
                "type": "text",
                "analyzer": "technical_analyzer"
            },
            
            # Vector embedding for semantic search
            "description_embedding": {
                "type": "dense_vector",
                "dims": 768,  # text-embedding-004 produces 768-dim vectors
                "index": True,
                "similarity": "cosine"
            },
            
            # Incident classification
            "severity": {
                "type": "keyword"
            },
            "incident_type": {
                "type": "keyword"  # database/network/application/infrastructure
            },
            "status": {
                "type": "keyword"  # open/investigating/resolved
            },
            
            # Technical details
            "affected_systems": {
                "type": "keyword"
            },
            "error_messages": {
                "type": "text",
                "analyzer": "technical_analyzer"
            },
            "stack_trace": {
                "type": "text",
                "index": False  # Don't search, just store
            },
            "technical_terms": {
                "type": "keyword"
            },
            
            # Resolution information
            "resolution_steps": {
                "type": "text",
                "analyzer": "technical_analyzer"
            },
            "resolution_time_minutes": {
                "type": "integer"
            },
            "root_cause": {
                "type": "text"
            },
            
            # Source metadata
            "source_type": {
                "type": "keyword"  # incident/log/documentation/slack
            },
            "source_url": {
                "type": "keyword",
                "index": False
            },
            
            # Temporal data
            "created_at": {
                "type": "date"
            },
            "resolved_at": {
                "type": "date"
            },
            "updated_at": {
                "type": "date"
            },
            
            # Additional metadata
            "tags": {
                "type": "keyword"
            },
            "related_incidents": {
                "type": "keyword"
            }
        }
    }
}

def create_index():
    """Create the Elasticsearch index with hybrid search support"""
    try:
        # Delete if exists (for development)
        if es.indices.exists(index=INDEX_NAME):
            print(f"Index {INDEX_NAME} exists. Deleting...")
            es.indices.delete(index=INDEX_NAME)
        
        # Create index
        es.indices.create(index=INDEX_NAME, body=INDEX_MAPPING)
        print(f"✅ Index '{INDEX_NAME}' created successfully!")
        
        # Verify
        info = es.indices.get(index=INDEX_NAME)
        print(f"✅ Index verified. Mapping: {info[INDEX_NAME]['mappings']}")
        
    except Exception as e:
        print(f"❌ Error creating index: {e}")
        raise

if __name__ == "__main__":
    create_index()
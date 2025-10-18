import json
from elasticsearch import Elasticsearch, helpers
from vertexai.generative_models import GenerativeModel
import vertexai
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize
vertexai.init(
    project=os.getenv('GOOGLE_CLOUD_PROJECT'),
    location=os.getenv('GOOGLE_CLOUD_REGION')
)

es = Elasticsearch(
    cloud_id=os.getenv('ELASTIC_CLOUD_ID'),
    api_key=os.getenv('ELASTIC_API_KEY')
)

embedding_model = GenerativeModel("text-embedding-004")

def generate_embedding(text: str):
    """Generate embedding using Vertex AI"""
    response = embedding_model.generate_content(text)
    return response.embeddings[0].values

def ingest_incidents(file_path: str):
    """Ingest incidents into Elasticsearch with embeddings"""
    
    # Load incidents
    with open(file_path, 'r') as f:
        incidents = json.load(f)
    
    print(f"📥 Ingesting {len(incidents)} incidents...")
    
    # Prepare bulk actions
    actions = []
    for incident in incidents:
        # Generate embedding for description
        embedding_text = f"{incident['title']} {incident['description']} {incident['error_messages']}"
        embedding = generate_embedding(embedding_text)
        
        # Add embedding to incident
        incident['description_embedding'] = embedding
        
        # Create action for bulk API
        action = {
            "_index": os.getenv('ELASTIC_INDEX_NAME', 'devops-incidents'),
            "_id": incident['incident_id'],
            "_source": incident
        }
        actions.append(action)
        print(f"✓ Processed {incident['incident_id']}")
    
    # Bulk index
    success, failed = helpers.bulk(es, actions, raise_on_error=False)
    
    print(f"\n✅ Ingestion complete!")
    print(f"   Successful: {success}")
    print(f"   Failed: {failed}")
    
    # Verify
    count = es.count(index=os.getenv('ELASTIC_INDEX_NAME'))
    print(f"   Total documents in index: {count['count']}")

if __name__ == "__main__":
    ingest_incidents('sample_incidents.json')
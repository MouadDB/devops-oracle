import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

def test_analyze_incident():
    """Test incident analysis"""
    print("Testing /api/v1/incidents/analyze endpoint...")
    
    incident = {
        "description": """
        Users reporting 500 errors on checkout page during peak traffic.
        Error logs show: HikariCP - Connection is not available, request timed out after 30000ms.
        Database connection pool appears exhausted. Current pool size is 20.
        This started happening after the Black Friday sale began.
        """,
        "user_id": "test_user_123"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/incidents/analyze",
        json=incident,
        timeout=60
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n=== ANALYSIS ===")
        print(json.dumps(result['analysis'], indent=2))
        
        print("\n=== TOP 3 SEARCH RESULTS ===")
        for i, r in enumerate(result['search_results'][:3]):
            print(f"\n{i+1}. {r['title']} (Score: {r['similarity_score']:.2f})")
            print(f"   {r['incident_id']} - {r['severity']} - {r['incident_type']}")
        
        print("\n=== RECOMMENDATION ===")
        rec = result['recommendation']
        print(f"Confidence: {rec['confidence_score']:.0%}")
        print(f"Estimated Time: {rec['estimated_resolution_time_minutes']} minutes")
        print(f"\nImmediate Actions:")
        for action in rec['immediate_actions']:
            print(f"  - {action}")
        
        print(f"\nProcessing time: {result['processing_time_seconds']}s")
        print(f"Agent steps: {', '.join(result['agent_steps'])}")
    else:
        print(f"Error: {response.text}")
    print()

def test_stats():
    """Test stats endpoint"""
    print("Testing /api/v1/stats endpoint...")
    response = requests.get(f"{BASE_URL}/api/v1/stats")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

if __name__ == "__main__":
    print("=== DevOps Oracle API Tests ===\n")
    
    test_health()
    test_stats()
    test_analyze_incident()
    
    print("=== All tests complete ===")
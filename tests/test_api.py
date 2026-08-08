import json
import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def load_root_json(filename: str):
    path = os.path.join(os.path.dirname(__file__), "..", filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def test_health_check():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_technical_spec_unified_api_flow():
    """Test POST /api/interview using candidates.json structure per technical-spec.md"""
    candidates_data = load_root_json("candidates.json")
    assert candidates_data is not None
    
    cand = candidates_data["candidates"][0] # Sarah Johnson
    session_id = "test-session-sarah-123"

    # Turn 1: Start Interview
    start_payload = {
        "sessionId": session_id,
        "candidate": cand
    }
    res1 = client.post("/api/interview", json=start_payload)
    assert res1.status_code == 200
    data1 = res1.json()
    assert "reply" in data1
    assert data1["done"] is False
    assert len(data1["reply"]) > 10

    # Turn 2: Conversation Turn
    answer_payload = {
        "sessionId": session_id,
        "message": "Vector embeddings represent text in dense high-dimensional space. We use HNSW vector indexes in vector databases like Qdrant to perform fast cosine similarity search."
    }
    res2 = client.post("/api/interview", json=answer_payload)
    assert res2.status_code == 200
    data2 = res2.json()
    assert "reply" in data2
    assert "done" in data2

def test_granular_interview_lifecycle():
    curr = {
        "days": [
            {
                "day": 1,
                "title": "Python Basics",
                "topics": [{"name": "GIL & Concurrency", "content": "The GIL locks execution to one thread."}]
            }
        ]
    }
    cand = {"name": "Test User", "experience_years": 3}
    
    start_payload = {
        "curriculum": curr,
        "candidate_profile": cand,
        "technical_specification": "Backend Software Developer"
    }
    
    res_start = client.post("/interview/start", json=start_payload)
    assert res_start.status_code == 200
    data_start = res_start.json()
    
    sid = data_start["session_id"]
    
    res_status = client.get(f"/interview/status/{sid}")
    assert res_status.status_code == 200
    assert res_status.json()["questions_asked"] == 1
    
    res_end = client.post("/interview/end", json={"session_id": sid})
    assert res_end.status_code == 200
    assert res_end.json()["status"] == "completed"

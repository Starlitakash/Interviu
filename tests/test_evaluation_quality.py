import json
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Helper custom curriculum to run deterministic, fast tests
TEST_CURRICULUM = {
    "days": [
        {
            "day": 1,
            "title": "Python Basics",
            "objectives": ["Understand GIL", "Know concurrency models"],
            "tools": ["multiprocessing", "threading"],
            "topics": [
                {
                    "name": "GIL & Concurrency",
                    "content": "The Global Interpreter Lock (GIL) is a mutex that protects access to Python objects, preventing multiple threads from executing Python bytecodes at once. This lock is necessary because CPython's memory management is not thread-safe. Multiprocessing bypasses the GIL by using separate memory spaces and processes."
                }
            ]
        },
        {
            "day": 2,
            "title": "Docker Containers",
            "objectives": ["Understand containerization", "Build docker images"],
            "tools": ["docker", "dockerfile"],
            "topics": [
                {
                    "name": "Docker Basics",
                    "content": "Docker containerizes applications. A Dockerfile specifies the base image, environment variables, dependencies, and execution commands to build a reproducible container image."
                }
            ]
        },
        {
            "day": 3,
            "title": "Kubernetes Deployment",
            "objectives": ["Understand Kubernetes", "Deploy pods"],
            "tools": ["kubectl", "yaml"],
            "topics": [
                {
                    "name": "Kubernetes Orchestration",
                    "content": "Kubernetes manages containerized workloads. Deployments define replica counts and update strategies, while Services expose pods to network traffic."
                }
            ]
        },
        {
            "day": 4,
            "title": "Vector Databases",
            "objectives": ["Understand vector search", "Index high-dimensional data"],
            "tools": ["qdrant", "hnsw"],
            "topics": [
                {
                    "name": "Vector Retrieval",
                    "content": "Vector databases like Qdrant index high-dimensional embeddings. The HNSW algorithm performs fast approximate nearest neighbor search."
                }
            ]
        }
    ]
}

def run_interview_scenario(candidate_name: str, answers_map: dict) -> dict:
    """Helper to run a full interview lifecycle, selecting answers based on the current question's topic."""
    # 1. Start the interview
    start_payload = {
        "curriculum": TEST_CURRICULUM,
        "candidate_profile": {
            "name": candidate_name,
            "experience_years": 3
        },
        "technical_specification": "Software Engineer with Python and Docker knowledge"
    }
    
    res_start = client.post("/interview/start", json=start_payload)
    assert res_start.status_code == 200
    data_start = res_start.json()
    session_id = data_start["session_id"]
    
    current_topic = data_start["question"]["topic"]
    
    # We will submit answers for 5 turns
    for turn in range(5):
        # Select answer based on topic (default to "ok")
        ans = answers_map.get(current_topic, "ok")
        
        res_ans = client.post("/interview/answer", json={
            "session_id": session_id,
            "answer": ans
        })
        assert res_ans.status_code == 200
        data_ans = res_ans.json()
        
        if data_ans.get("status") == "completed":
            return data_ans["feedback"]
            
        current_topic = data_ans["next_question"]["topic"]
        
    # 3. End the interview to get the final report
    res_end = client.post("/interview/end", json={"session_id": session_id})
    assert res_end.status_code == 200
    return res_end.json()["feedback"]

def test_quality_low_answers():
    """Test 1: All answers = 'ok'. Expected overall score < 20% (2.0) and NO_HIRE."""
    answers_map = {
        "Python Basics": "ok",
        "Docker Containers": "ok",
        "Kubernetes Deployment": "ok",
        "Vector Databases": "ok"
    }
    feedback = run_interview_scenario("Sarah Johnson", answers_map)
    
    overall_score = feedback["overall_score"]
    rec = feedback["hiring_recommendation"]
    
    print(f"\n[Test 1] Score: {overall_score}, Recommendation: {rec}")
    assert overall_score < 2.0
    assert rec == "no_hire"

def test_quality_average_answers():
    """Test 2: Average answers. Expected overall score between 40% and 60% (4.0 - 6.0) and WEAK_HIRE."""
    answers_map = {
        "Python Basics": "The GIL is a global interpreter lock in Python. It allows only one thread to run at a time, making it single threaded.",
        "Docker Containers": "Docker is used to containerize applications, so they run the same everywhere. You write a dockerfile and build an image.",
        "Kubernetes Deployment": "Kubernetes manages containers. It helps scale pods up and down, and uses services to route traffic.",
        "Vector Databases": "Vector databases index vector embeddings of text. They are used for fast similarity searches using algorithms like HNSW."
    }
    feedback = run_interview_scenario("David Smith", answers_map)
    
    overall_score = feedback["overall_score"]
    rec = feedback["hiring_recommendation"]
    
    print(f"\n[Test 2] Score: {overall_score}, Recommendation: {rec}")
    assert 4.0 <= overall_score <= 6.0
    assert rec == "weak_hire"

def test_quality_excellent_answers():
    """Test 3: Excellent answers. Expected overall score between 80% and 95% (8.0 - 9.5) and HIRE/STRONG_HIRE."""
    answers_map = {
        "Python Basics": "The Global Interpreter Lock (GIL) in CPython is a mutex that prevents multiple native threads from executing Python bytecodes concurrently. This is essential because CPython's memory management is not thread-safe. To achieve true concurrency for CPU-bound tasks, we bypass the GIL using multiprocessing to spawn separate processes with their own memory spaces, or use alternative runtimes like Jython.",
        "Docker Containers": "Docker containerizes apps using Linux namespaces and cgroups for process isolation. A Dockerfile is a text document containing instructions to build an image. We use multi-stage builds to optimize image size by separating the build environment from the final runtime container.",
        "Kubernetes Deployment": "Kubernetes is a container orchestration platform. Deployments manage stateless pods declaratively, defining replica sets, rolling updates, and health checks. Services expose these pods to traffic using virtual IPs and load balancing across select label selectors.",
        "Vector Databases": "Vector databases like Qdrant are designed to store and query high-dimensional vector embeddings generated by machine learning models. They index data using Hierarchical Navigable Small World (HNSW) graphs to achieve sub-millisecond approximate nearest neighbor (ANN) search latency, and combine this with scalar filtering."
    }
    feedback = run_interview_scenario("Emily Davis", answers_map)
    
    overall_score = feedback["overall_score"]
    rec = feedback["hiring_recommendation"]
    
    print(f"\n[Test 3] Score: {overall_score}, Recommendation: {rec}")
    assert 8.0 <= overall_score <= 9.5
    assert rec in ["hire", "strong_hire"]

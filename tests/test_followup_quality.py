import json
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Helper custom curriculum to run deterministic, fast tests
TEST_CURRICULUM = {
    "days": [
        {
            "day": 12,
            "title": "Prompt Engineering",
            "objectives": ["Understand prompt versioning and A/B testing", "Know prompt templates"],
            "tools": ["git", "jinja"],
            "topics": [
                {
                    "name": "Prompt Versioning",
                    "content": "Prompt engineering versioning involves using Git to track changes in prompt templates. A/B testing evaluates prompt variants by measuring latency and user response accuracy in production."
                }
            ]
        }
    ]
}

def get_followup_question(candidate_name: str, answer_turn1: str) -> dict:
    """Helper to start interview, submit answer_turn1, and return the follow-up question object."""
    # 1. Start the interview
    start_payload = {
        "curriculum": TEST_CURRICULUM,
        "candidate_profile": {
            "name": candidate_name,
            "experience_years": 3,
            "jobRole": "Software Engineer"
        },
        "technical_specification": "Software Engineer with prompt design skills"
    }
    
    res_start = client.post("/interview/start", json=start_payload)
    assert res_start.status_code == 200
    data_start = res_start.json()
    session_id = data_start["session_id"]
    
    # 2. Submit candidate's answer for turn 1
    res_ans = client.post("/interview/answer", json={
        "session_id": session_id,
        "answer": answer_turn1
    })
    assert res_ans.status_code == 200
    data_ans = res_ans.json()
    
    # Return next question details
    return {
        "text": data_ans["next_question"]["text"],
        "context_bridge": data_ans["next_question"].get("context_bridge", ""),
        "topic": data_ans["next_question"]["topic"]
    }

def test_followup_empty_answer():
    """TEST 1: Candidate answer = '' (Empty/Meaningless). Expected no building on previous, no fabricated concepts, natural recovery bridge."""
    result = get_followup_question("John Doe", "")
    full_q = f"{result['context_bridge']} {result['text']}".strip()
    print(f"\n[TEST 1] Follow-up for Empty Answer:\n{full_q}")
    
    # Verify no generic follow-up wording
    for forbidden in ["building on", "you mentioned", "solid foundation", "you touched on", "interesting points"]:
        assert forbidden not in full_q.lower(), f"Forbidden phrase '{forbidden}' found in question."
    
    # Verify presence of natural recovery keywords
    recovery_words = ["try", "cover", "simpler", "basic", "angle", "first", "again"]
    assert any(w in full_q.lower() for w in recovery_words), "No natural recovery wording detected."

def test_followup_ok_answer():
    """TEST 2: Candidate answer = 'ok'. Expected no building on previous, no fabricated concepts, natural recovery bridge."""
    result = get_followup_question("Jane Doe", "ok")
    full_q = f"{result['context_bridge']} {result['text']}".strip()
    print(f"\n[TEST 2] Follow-up for 'ok' Answer:\n{full_q}")
    
    for forbidden in ["building on", "you mentioned", "solid foundation", "you touched on", "interesting points"]:
        assert forbidden not in full_q.lower(), f"Forbidden phrase '{forbidden}' found in question."
        
    recovery_words = ["try", "cover", "simpler", "basic", "angle", "first", "again"]
    assert any(w in full_q.lower() for w in recovery_words), "No natural recovery wording detected."

def test_followup_idk_answer():
    """TEST 3: Candidate answer = 'I don't know'. Expected supportive clarification or simpler question."""
    result = get_followup_question("Bob Martin", "I don't know")
    full_q = f"{result['context_bridge']} {result['text']}".strip()
    print(f"\n[TEST 3] Follow-up for 'I don't know' Answer:\n{full_q}")
    
    for forbidden in ["building on", "you mentioned", "solid foundation", "you touched on", "interesting points"]:
        assert forbidden not in full_q.lower(), f"Forbidden phrase '{forbidden}' found in question."

def test_followup_partial_answer():
    """TEST 4: Candidate gives partially correct answer mentioning ONLY 'prompt templates'. Expected no fabrication of versioning/testing."""
    result = get_followup_question("Alice Smith", "I only know about prompt templates, which are reusable static strings.")
    full_q = f"{result['context_bridge']} {result['text']}".strip()
    print(f"\n[TEST 4] Follow-up for Partial Answer (only prompt templates):\n{full_q}")
    
    # Follow-up must NOT claim candidate discussed versioning, A/B testing, or latency
    for forbidden in ["versioning", "a/b testing", "latency", "variant"]:
        assert forbidden not in result['context_bridge'].lower(), f"Fabricated concept '{forbidden}' found in transition bridge."

def test_followup_strong_answer():
    """TEST 5: Candidate gives strong answer mentioning prompt versioning and A/B testing."""
    result = get_followup_question("Charlie Brown", "I manage templates via git versioning. In production, I run A/B testing to measure prompt latency and variants.")
    full_q = f"{result['context_bridge']} {result['text']}".strip()
    print(f"\n[TEST 5] Follow-up for Strong Answer:\n{full_q}")
    
    # Strong response should naturally flow or explore deeper implementation details
    assert any(phrase in full_q.lower() for phrase in ["building", "mentioned", "explore", "versioning", "testing", "scale"]), "Strong answer did not trigger a deeper follow-up."

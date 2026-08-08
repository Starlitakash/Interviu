from app.evaluation.difficulty import adjust_difficulty, score_to_difficulty

def test_score_to_difficulty():
    assert score_to_difficulty(0.9) == "hard"
    assert score_to_difficulty(0.75) == "medium_plus"
    assert score_to_difficulty(0.55) == "medium"
    assert score_to_difficulty(0.35) == "easy"
    assert score_to_difficulty(0.1) == "very_easy"

def test_adjust_difficulty_consistency_increase():
    state = {
        "current_difficulty": "medium",
        "consecutive_good": 0,
        "consecutive_bad": 0
    }
    # 1st good answer -> counter becomes 1, difficulty stays medium
    diff1 = adjust_difficulty(state, latest_score=0.8)
    assert diff1 == "medium"
    assert state["consecutive_good"] == 1
    
    # 2nd good answer -> counter hits 2, difficulty increases to medium_plus
    diff2 = adjust_difficulty(state, latest_score=0.85)
    assert diff2 == "medium_plus"
    assert state["consecutive_good"] == 0

def test_adjust_difficulty_single_bad_decrease():
    state = {
        "current_difficulty": "medium_plus",
        "consecutive_good": 0,
        "consecutive_bad": 0
    }
    # 1 bad answer -> immediately drops to medium
    diff = adjust_difficulty(state, latest_score=0.2)
    assert diff == "medium"

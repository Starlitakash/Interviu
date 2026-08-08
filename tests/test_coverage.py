from app.evaluation.coverage import update_days_covered, is_coverage_guaranteed

def test_update_days_covered_idempotent():
    days = []
    days = update_days_covered(days, "Day 1")
    days = update_days_covered(days, "Day 1")
    days = update_days_covered(days, "Day 2")
    assert days == ["Day 1", "Day 2"]

def test_is_coverage_guaranteed():
    # 4 days covered out of min 4 -> True
    assert is_coverage_guaranteed(days_covered_count=4, questions_asked=5, question_budget=8) == True
    
    # 2 days covered, 4 questions remaining (need 2 more days) -> True
    assert is_coverage_guaranteed(days_covered_count=2, questions_asked=4, question_budget=8) == True
    
    # 1 day covered, 2 questions remaining (need 3 more days) -> False (risk!)
    assert is_coverage_guaranteed(days_covered_count=1, questions_asked=7, question_budget=8) == False

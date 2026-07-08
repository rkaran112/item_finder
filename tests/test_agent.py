from agent import classify_score


def test_classify_score_confident_match():
    assert classify_score(0.45) == "Found, no need for human review"
    assert classify_score(0.9) == "Found, no need for human review"


def test_classify_score_needs_review():
    assert classify_score(0.20) == "Needs human review"
    assert classify_score(0.44) == "Needs human review"


def test_classify_score_not_found():
    assert classify_score(0.19) == "Item not found"
    assert classify_score(0.0) == "Item not found"

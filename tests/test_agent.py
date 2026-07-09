import pandas as pd
import pytest

from agent import classify_score, process_excel


def test_classify_score_confident_match():
    assert classify_score(0.45) == "Found, no need for human review"
    assert classify_score(0.9) == "Found, no need for human review"


def test_classify_score_needs_review():
    assert classify_score(0.20) == "Needs human review"
    assert classify_score(0.44) == "Needs human review"


def test_classify_score_not_found():
    assert classify_score(0.19) == "Item not found"
    assert classify_score(0.0) == "Item not found"


@pytest.fixture
def tmp_xlsx(tmp_path):
    def _write(columns_and_rows):
        path = tmp_path / "input.xlsx"
        pd.DataFrame(columns_and_rows).to_excel(path, index=False)
        return str(path)
    return _write


def test_process_excel_rejects_missing_required_columns(tmp_xlsx):
    input_file = tmp_xlsx({'GeM Title': ['Widget'], 'GeM Brand': ['Acme']})

    assert process_excel(input_file) is None


def test_process_excel_rejects_when_all_required_columns_missing(tmp_xlsx):
    input_file = tmp_xlsx({'Some Other Column': ['value']})

    assert process_excel(input_file) is None

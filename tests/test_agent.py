import pandas as pd
import pytest

import agent
from agent import classify_score, process_excel, search_product


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


class FakeDDGS:
    def __init__(self, results):
        self._results = results

    def __call__(self, *args, **kwargs):
        return self

    def text(self, query, max_results=10):
        return self._results


def test_search_product_ignores_links_outside_amazon_and_flipkart(monkeypatch):
    monkeypatch.setattr(agent, 'DDGS', FakeDDGS([
        {'href': 'https://example.com/widget', 'title': 'Acme Widget X1'},
    ]))

    link, score = search_product('Widget X1', 'Acme', 'X1')

    assert link is None
    assert score == 0.0


def test_search_product_picks_best_matching_result(monkeypatch):
    monkeypatch.setattr(agent, 'DDGS', FakeDDGS([
        {'href': 'https://www.amazon.in/dp/1', 'title': 'Totally unrelated product'},
        {'href': 'https://www.flipkart.com/p/2', 'title': 'Acme Widget X1'},
    ]))

    link, score = search_product('Widget X1', 'Acme', 'X1')

    assert link == 'https://www.flipkart.com/p/2'
    assert score > 0.85


def test_search_product_returns_none_when_ddgs_raises(monkeypatch):
    class RaisingDDGS:
        def __call__(self, *args, **kwargs):
            return self

        def text(self, query, max_results=10):
            raise RuntimeError('search backend unavailable')

    monkeypatch.setattr(agent, 'DDGS', RaisingDDGS())

    link, score = search_product('Widget X1', 'Acme', 'X1')

    assert link is None
    assert score == 0.0

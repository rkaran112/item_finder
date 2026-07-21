import pandas as pd
import pytest

import agent
from agent import classify_score, clean_field, process_excel, search_product


def test_classify_score_confident_match():
    assert classify_score(0.45) == "Found, no need for human review"
    assert classify_score(0.9) == "Found, no need for human review"


def test_classify_score_needs_review():
    assert classify_score(0.20) == "Needs human review"
    assert classify_score(0.44) == "Needs human review"


def test_classify_score_not_found():
    assert classify_score(0.19) == "Item not found"
    assert classify_score(0.0) == "Item not found"


def test_clean_field_treats_missing_values_as_empty():
    assert clean_field(float('nan')) == ''
    assert clean_field(None) == ''


def test_clean_field_stringifies_and_strips_present_values():
    assert clean_field('  Acme  ') == 'Acme'
    assert clean_field(42) == '42'


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


def test_process_excel_row_loop_populates_result_columns(tmp_xlsx, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(agent, 'sleep', lambda seconds: None)

    input_file = tmp_xlsx({
        'GeM Title': ['Widget X1', 'Gadget Y2'],
        'GeM Brand': ['Acme', 'Beta'],
        'GeM Model': ['X1', 'Y2'],
    })

    responses = {
        ('Acme', 'X1', 'Widget X1'): ('https://www.amazon.in/dp/1', 0.9),
        ('Beta', 'Y2', 'Gadget Y2'): (None, 0.0),
    }
    monkeypatch.setattr(
        agent, 'search_product',
        lambda title, brand, model: responses[(brand, model, title)],
    )

    output_file = process_excel(input_file)

    assert output_file is not None
    # keep_default_na=False so pandas doesn't read our literal "N/A" placeholder back as NaN
    result = pd.read_excel(output_file, keep_default_na=False)
    assert list(result['Amazon/Flipkart Link']) == ['https://www.amazon.in/dp/1', 'N/A']
    assert list(result['Similarity Score']) == [0.9, 0.0]
    assert list(result['Review Status']) == [
        'Found, no need for human review',
        'Item not found',
    ]


def test_main_uses_default_file_when_input_is_blank(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'sample_products.xlsx').write_text('placeholder')
    monkeypatch.setattr('builtins.input', lambda prompt='': '')
    calls = []
    monkeypatch.setattr(agent, 'process_excel', lambda path: calls.append(path))

    agent.main()

    assert calls == ['sample_products.xlsx']


def test_main_reports_error_and_skips_processing_for_missing_file(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr('builtins.input', lambda prompt='': 'does_not_exist.xlsx')
    calls = []
    monkeypatch.setattr(agent, 'process_excel', lambda path: calls.append(path))

    agent.main()

    assert calls == []
    assert "Could not find the file" in capsys.readouterr().out


def test_main_processes_the_given_file_path(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    given_file = tmp_path / 'custom.xlsx'
    given_file.write_text('placeholder')
    monkeypatch.setattr('builtins.input', lambda prompt='': str(given_file))
    calls = []
    monkeypatch.setattr(agent, 'process_excel', lambda path: calls.append(path))

    agent.main()

    assert calls == [str(given_file)]


def test_process_excel_treats_blank_cells_as_empty_not_literal_nan(tmp_xlsx, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(agent, 'sleep', lambda seconds: None)

    input_file = tmp_xlsx({
        'GeM Title': ['Widget X1'],
        'GeM Brand': ['Acme'],
        'GeM Model': [None],
    })

    calls = []

    def fake_search_product(title, brand, model):
        calls.append((title, brand, model))
        return None, 0.0

    monkeypatch.setattr(agent, 'search_product', fake_search_product)

    process_excel(input_file)

    assert calls == [('Widget X1', 'Acme', '')]

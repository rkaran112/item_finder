import os

import pytest

from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.mark.parametrize('filename', [
    'search_results.xlsx',
    'not_a_results_file.xlsx',
    'search_results_20240101_120000.txt',
    '../secret.xlsx',
])
def test_download_rejects_non_matching_filenames(client, filename):
    response = client.get(f'/download/{filename}')
    # Filenames that don't fit the pattern we generate ourselves must never
    # reach send_file(); Flask's routing (no slash allowed) or our own
    # regex check should stop them first.
    assert response.status_code in (400, 404)


def test_download_accepts_expected_filename_pattern(client):
    filename = 'search_results_20240101_120000.xlsx'
    filepath = os.path.join(app.root_path, filename)
    with open(filepath, 'w') as f:
        f.write('data')

    try:
        response = client.get(f'/download/{filename}')
        assert response.status_code == 200
    finally:
        os.remove(filepath)

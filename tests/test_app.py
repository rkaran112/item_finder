import io
import os

import pytest

import app as app_module
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_process_flashes_error_when_no_file_part(client):
    response = client.post('/process', data={}, content_type='multipart/form-data', follow_redirects=True)

    assert response.status_code == 200
    assert b'No file part provided.' in response.data


def test_process_flashes_error_when_no_file_selected(client):
    data = {'file': (io.BytesIO(b''), '')}
    response = client.post('/process', data=data, content_type='multipart/form-data', follow_redirects=True)

    assert response.status_code == 200
    assert b'No file selected.' in response.data


def test_process_flashes_error_for_invalid_extension(client):
    data = {'file': (io.BytesIO(b'dummy content'), 'Products.txt')}
    response = client.post('/process', data=data, content_type='multipart/form-data', follow_redirects=True)

    assert response.status_code == 200
    assert b'Invalid file format' in response.data


def test_process_flashes_error_when_process_excel_fails(client, monkeypatch):
    monkeypatch.setattr(app_module, 'process_excel', lambda filepath: None)

    data = {'file': (io.BytesIO(b'dummy content'), 'Products.xlsx')}
    response = client.post('/process', data=data, content_type='multipart/form-data', follow_redirects=True)

    assert response.status_code == 200
    assert b'Error processing file' in response.data


def test_process_accepts_uppercase_xlsx_extension(client, monkeypatch):
    monkeypatch.setattr(app_module, 'process_excel', lambda filepath: 'search_results_20240101_120000.xlsx')

    data = {'file': (io.BytesIO(b'dummy content'), 'Products.XLSX')}
    response = client.post('/process', data=data, content_type='multipart/form-data')

    assert response.status_code == 200
    assert b'Invalid file format' not in response.data


def test_process_removes_uploaded_file_after_processing(client, monkeypatch):
    monkeypatch.setattr(app_module, 'process_excel', lambda filepath: 'search_results_20240101_120000.xlsx')

    data = {'file': (io.BytesIO(b'dummy content'), 'Products.xlsx')}
    response = client.post('/process', data=data, content_type='multipart/form-data')

    assert response.status_code == 200
    assert os.listdir(app.config['UPLOAD_FOLDER']) == []


def test_process_gives_concurrent_uploads_of_the_same_filename_distinct_paths(client, monkeypatch):
    seen_filepaths = []
    monkeypatch.setattr(
        app_module, 'process_excel',
        lambda filepath: seen_filepaths.append(filepath) or 'search_results_20240101_120000.xlsx',
    )

    for _ in range(2):
        data = {'file': (io.BytesIO(b'dummy content'), 'Products.xlsx')}
        response = client.post('/process', data=data, content_type='multipart/form-data')
        assert response.status_code == 200

    assert len(seen_filepaths) == 2
    assert seen_filepaths[0] != seen_filepaths[1]


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


def test_download_returns_404_for_missing_file(client):
    # Matches the expected pattern but was never actually generated (e.g. a
    # stale link after a restart) - should 404, not crash with a 500.
    response = client.get('/download/search_results_20990101_120000.xlsx')
    assert response.status_code == 404


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

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
    uploaded_path = os.path.join(app.config['UPLOAD_FOLDER'], 'Products.xlsx')
    assert not os.path.exists(uploaded_path)


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

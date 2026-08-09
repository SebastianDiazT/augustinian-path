import pytest

pytestmark = pytest.mark.urls('apps.core.tests.urlconf')


def test_wraps_a_plain_detail_response(client):
    response = client.get('/detail/')

    assert response.status_code == 200
    body = response.json()
    assert body['data'] == {'id': 1, 'nombre': 'Test'}
    assert 'request_id' in body['meta']
    assert 'pagination' not in body['meta']


def test_does_not_double_wrap_a_paginated_response(client):
    response = client.get('/paginated/')

    body = response.json()
    assert set(body.keys()) == {'data', 'meta'}
    assert 'pagination' in body['meta']


def test_does_not_wrap_an_error_response(client):
    response = client.get('/not-found/')

    body = response.json()
    assert 'error' in body
    assert 'data' not in body

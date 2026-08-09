import pytest


@pytest.mark.django_db
def test_health_check_returns_200_ok(client):
    response = client.get('/api/v1/health/')

    assert response.status_code == 200
    body = response.json()
    assert body['data']['status'] == 'ok'
    assert body['data']['database'] == 'ok'
    assert 'request_id' in body['meta']


@pytest.mark.django_db
def test_health_check_does_not_require_authentication(client):
    response = client.get('/api/v1/health/')
    assert response.status_code != 401
    assert response.status_code != 403


@pytest.mark.django_db
def test_health_check_returns_503_when_database_is_unreachable(client, monkeypatch):
    from django.db import connection

    def _raise(*args, **kwargs):
        raise Exception('no se pudo conectar a la base de datos')

    monkeypatch.setattr(connection, 'ensure_connection', _raise)

    response = client.get('/api/v1/health/')

    assert response.status_code == 503
    body = response.json()
    assert body['data']['status'] == 'degraded'
    assert body['data']['database'] == 'error'

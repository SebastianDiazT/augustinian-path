import pytest


def test_unmatched_url_returns_json_envelope_not_django_html(client):
    response = client.get('/api/v1/this-route-does-not-exist/')

    assert response.status_code == 404
    assert response['Content-Type'].startswith('application/json')
    body = response.json()
    assert body['error']['code'] == 'NOT_FOUND'
    assert body['error']['request_id']


@pytest.mark.urls('apps.core.tests.urlconf')
def test_plain_django_view_unhandled_exception_returns_json_500(client):
    client.raise_request_exception = False

    response = client.get('/plain-500/')

    assert response.status_code == 500
    assert response['Content-Type'].startswith('application/json')
    body = response.json()
    assert body['error']['code'] == 'INTERNAL_ERROR'

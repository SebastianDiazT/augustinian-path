import pytest

pytestmark = pytest.mark.urls('apps.core.tests.urlconf')


def test_validation_error_returns_400_with_field_details(client):
    response = client.get('/validation-error/')

    assert response.status_code == 400
    body = response.json()
    error = body['error']
    assert error['code'] == 'VALIDATION_ERROR'
    assert isinstance(error['details'], list)
    assert error['details'] == [{'field': 'nombre', 'message': 'Este campo es requerido'}]
    assert error['request_id']


def test_not_found_returns_404(client):
    response = client.get('/not-found/')

    assert response.status_code == 404
    error = response.json()['error']
    assert error['code'] == 'NOT_FOUND'
    assert error['details'] == []
    assert error['request_id']


def test_permission_denied_returns_403(client):
    response = client.get('/permission-denied/')

    assert response.status_code == 403
    assert response.json()['error']['code'] == 'PERMISSION_DENIED'


def test_not_authenticated_returns_401(client):
    response = client.get('/not-authenticated/')

    assert response.status_code == 401
    assert response.json()['error']['code'] == 'NOT_AUTHENTICATED'


def test_unhandled_exception_returns_500_with_generic_message(client):
    client.raise_request_exception = False

    response = client.get('/unhandled/')

    assert response.status_code == 500
    error = response.json()['error']
    assert error['code'] == 'INTERNAL_ERROR'
    # nunca se debe exponer el traceback ni el detalle interno
    assert 'boom' not in error['message']
    assert 'RuntimeError' not in error['message']
    assert error['request_id']


def test_error_details_is_always_a_list_never_null(client):
    for path in ('/not-found/', '/permission-denied/', '/not-authenticated/'):
        response = client.get(path)
        assert response.json()['error']['details'] == []

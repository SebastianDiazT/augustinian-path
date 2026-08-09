import pytest

pytestmark = pytest.mark.urls('apps.core.tests.urlconf')


def test_default_page_size_and_shape(client):
    response = client.get('/paginated/')

    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {'data', 'meta'}
    assert len(body['data']) == 20

    pagination = body['meta']['pagination']
    assert pagination['page'] == 1
    assert pagination['page_size'] == 20
    assert pagination['total_items'] == 97
    assert pagination['total_pages'] == 5
    assert pagination['has_next'] is True
    assert pagination['has_previous'] is False
    assert body['meta']['request_id']


def test_has_previous_true_on_second_page(client):
    response = client.get('/paginated/?page=2')

    pagination = response.json()['meta']['pagination']
    assert pagination['page'] == 2
    assert pagination['has_previous'] is True
    assert pagination['has_next'] is True


def test_last_page_has_next_false(client):
    response = client.get('/paginated/?page=5')

    pagination = response.json()['meta']['pagination']
    assert pagination['has_next'] is False
    assert pagination['has_previous'] is True
    # 97 items, page_size 20 -> última página con 17 items
    assert len(response.json()['data']) == 17


def test_page_size_query_param_is_respected(client):
    response = client.get('/paginated/?page_size=10')

    body = response.json()
    assert len(body['data']) == 10
    assert body['meta']['pagination']['page_size'] == 10


def test_page_size_is_capped_at_max_page_size(client):
    response = client.get('/paginated/?page_size=1000')

    body = response.json()
    assert body['meta']['pagination']['page_size'] == 100
    # solo hay 97 items en total, así que la página trae los 97
    assert len(body['data']) == 97
    assert body['meta']['pagination']['total_pages'] == 1

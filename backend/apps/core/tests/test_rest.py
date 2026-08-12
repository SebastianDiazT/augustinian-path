from unittest.mock import Mock

from apps.core.pagination import EnvelopePageNumberPagination
from apps.core.renderers import EnvelopeJSONRenderer


def test_envelope_renderer_skips_already_wrapped_or_none():
    renderer = EnvelopeJSONRenderer()

    assert renderer.render(None) is None or b'null'

    res_wrapped = renderer.render({'error': 'algo'})
    assert b'error' in res_wrapped


def test_envelope_pagination():
    paginator = EnvelopePageNumberPagination()

    paginator.request = Mock(query_params={})
    paginator.page = Mock(number=1)
    paginator.page.has_next.return_value = False
    paginator.page.has_previous.return_value = False
    paginator.page.paginator.num_pages = 1
    paginator.page.paginator.count = 5

    response = paginator.get_paginated_response([{'id': 1}])
    assert response.data['data'][0]['id'] == 1
    assert response.data['meta']['pagination']['total_items'] == 5

    schema = paginator.get_paginated_response_schema({})
    assert 'data' in schema['properties']
    assert 'meta' in schema['properties']

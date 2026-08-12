from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .context import get_request_id


class EnvelopePageNumberPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ('data', data),
                    (
                        'meta',
                        OrderedDict(
                            [
                                ('request_id', get_request_id()),
                                (
                                    'pagination',
                                    OrderedDict(
                                        [
                                            ('page', self.page.number),
                                            (
                                                'page_size',
                                                self.get_page_size(self.request),
                                            ),
                                            (
                                                'total_pages',
                                                self.page.paginator.num_pages,
                                            ),
                                            (
                                                'total_items',
                                                self.page.paginator.count,
                                            ),
                                            ('has_next', self.page.has_next()),
                                            (
                                                'has_previous',
                                                self.page.has_previous(),
                                            ),
                                        ],
                                    ),
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'data': {'type': 'array', 'items': schema},
                'meta': {
                    'type': 'object',
                    'properties': {
                        'request_id': {'type': 'string', 'format': 'uuid'},
                        'pagination': {
                            'type': 'object',
                            'properties': {
                                'page': {'type': 'integer'},
                                'page_size': {'type': 'integer'},
                                'total_pages': {'type': 'integer'},
                                'total_items': {'type': 'integer'},
                                'has_next': {'type': 'boolean'},
                                'has_previous': {'type': 'boolean'},
                            },
                        },
                    },
                },
            },
        }

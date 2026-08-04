from uuid import UUID

from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.test import APITestCase


class HealthEndpointTests(APITestCase):
    endpoint = '/api/v1/health/'

    def test_health_endpoint_returns_standard_response(self) -> None:
        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        body = response.json()

        self.assertEqual(
            body['data'],
            {
                'status': 'ok',
                'service': 'augustinian-path-backend',
            },
        )

        self.assertEqual(body['meta']['api_version'], 'v1')
        self.assertIsNotNone(parse_datetime(body['meta']['timestamp']))

        request_id = body['meta']['request_id']

        UUID(request_id)

        self.assertEqual(
            response.headers['X-Request-ID'],
            request_id,
        )

    def test_health_endpoint_preserves_valid_request_id(self) -> None:
        request_id = '70af3f98-1516-4f5d-b468-f8c61ae60b29'

        response = self.client.get(
            self.endpoint,
            headers={
                'X-Request-ID': request_id,
            },
        )

        self.assertEqual(
            response.json()['meta']['request_id'],
            request_id,
        )
        self.assertEqual(
            response.headers['X-Request-ID'],
            request_id,
        )

    def test_health_endpoint_returns_standard_method_error(
        self,
    ) -> None:
        response = self.client.post(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

        body = response.json()

        self.assertEqual(
            body['error']['type'],
            'urn:augustinian-path:problem:method-not-allowed',
        )
        self.assertEqual(
            body['error']['title'],
            'Método no permitido',
        )
        self.assertEqual(
            body['error']['status'],
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        self.assertEqual(
            body['error']['instance'],
            self.endpoint,
        )
        self.assertIsInstance(
            body['error']['detail'],
            str,
        )

        self.assertEqual(
            body['meta']['api_version'],
            'v1',
        )

        request_id = body['meta']['request_id']

        UUID(request_id)

        self.assertEqual(
            response.headers['X-Request-ID'],
            request_id,
        )

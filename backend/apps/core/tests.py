from unittest.mock import patch
from uuid import UUID

from django.test import SimpleTestCase
from django.utils.dateparse import parse_datetime
from drf_spectacular.generators import SchemaGenerator
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework.views import APIView


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


class UnexpectedErrorView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request: Request) -> Response:
        raise RuntimeError(
            'sensitive internal information',
        )


class UnhandledExceptionResponseTests(SimpleTestCase):
    @patch('apps.core.exceptions.logger.error')
    def test_returns_standard_internal_server_error(
        self,
        logger_error,
    ) -> None:
        request = APIRequestFactory().get(
            '/api/v1/failure/',
        )

        response = UnexpectedErrorView.as_view()(
            request,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

        body = response.data

        self.assertEqual(
            body['error'],
            {
                'type': ('urn:augustinian-path:problem:internal-server-error'),
                'title': 'Error interno del servidor',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'detail': ('Ha ocurrido un error interno del servidor.'),
                'instance': '/api/v1/failure/',
            },
        )
        self.assertEqual(
            body['meta']['api_version'],
            'v1',
        )
        self.assertNotIn(
            'sensitive internal information',
            str(body),
        )
        logger_error.assert_called_once()


class OpenApiSchemaTests(SimpleTestCase):
    def test_documents_internal_server_errors(
        self,
    ) -> None:
        schema = SchemaGenerator().get_schema(
            request=None,
            public=True,
        )

        operations = []

        for path, path_item in schema['paths'].items():
            for method in (
                'get',
                'post',
                'put',
                'patch',
                'delete',
            ):
                operation = path_item.get(method)

                if operation is not None:
                    operations.append(
                        (
                            path,
                            method,
                            operation,
                        )
                    )

        self.assertGreater(len(operations), 0)

        for path, method, operation in operations:
            with self.subTest(
                path=path,
                method=method,
            ):
                response = operation['responses']['500']

                self.assertEqual(
                    response['content']['application/json']['schema'],
                    {
                        '$ref': ('#/components/schemas/ApiErrorResponse'),
                    },
                )

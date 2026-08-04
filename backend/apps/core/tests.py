from types import SimpleNamespace
from unittest.mock import patch
from uuid import UUID, uuid4

from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.test import SimpleTestCase, override_settings
from django.urls import path as url_path
from django.utils.dateparse import parse_datetime
from drf_spectacular.generators import SchemaGenerator
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework.views import APIView

from apps.core.throttles import (
    AnonymousBurstRateThrottle,
    AnonymousSustainedRateThrottle,
    UserBurstRateThrottle,
    UserSustainedRateThrottle,
)


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
    def test_documents_standard_error_responses(
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
            for status_code in (
                '429',
                '500',
            ):
                with self.subTest(
                    path=path,
                    method=method,
                    status_code=status_code,
                ):
                    response = operation['responses'][status_code]

                    self.assertEqual(
                        response['content']['application/json']['schema'],
                        {
                            '$ref': ('#/components/schemas/ApiErrorResponse'),
                        },
                    )


class FirstThrottleTestView(APIView):
    pass


class SecondThrottleTestView(APIView):
    pass


class ApplicationThrottleTests(SimpleTestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()

    def test_uses_configured_rates(self) -> None:
        cases = (
            (
                AnonymousBurstRateThrottle,
                '120/min',
            ),
            (
                AnonymousSustainedRateThrottle,
                '5000/day',
            ),
            (
                UserBurstRateThrottle,
                '120/min',
            ),
            (
                UserSustainedRateThrottle,
                '2000/day',
            ),
        )

        for throttle_class, expected_rate in cases:
            with self.subTest(
                throttle_class=throttle_class,
            ):
                self.assertEqual(
                    throttle_class().rate,
                    expected_rate,
                )

    def test_anonymous_throttle_is_scoped_by_view(
        self,
    ) -> None:
        request = self.factory.get(
            '/api/v1/resource/',
        )
        request.user = AnonymousUser()

        throttle = AnonymousBurstRateThrottle()

        first_key = throttle.get_cache_key(
            request,
            FirstThrottleTestView(),
        )
        second_key = throttle.get_cache_key(
            request,
            SecondThrottleTestView(),
        )

        self.assertIsNotNone(first_key)
        self.assertIsNotNone(second_key)
        self.assertNotEqual(
            first_key,
            second_key,
        )

    def test_anonymous_throttles_ignore_authenticated_users(
        self,
    ) -> None:
        request = self.factory.get(
            '/api/v1/resource/',
        )
        request.user = SimpleNamespace(
            is_authenticated=True,
        )
        view = FirstThrottleTestView()

        for throttle_class in (
            AnonymousBurstRateThrottle,
            AnonymousSustainedRateThrottle,
        ):
            with self.subTest(
                throttle_class=throttle_class,
            ):
                self.assertIsNone(
                    throttle_class().get_cache_key(
                        request,
                        view,
                    )
                )

    def test_user_throttles_ignore_anonymous_users(
        self,
    ) -> None:
        request = self.factory.get(
            '/api/v1/resource/',
        )
        request.user = AnonymousUser()
        view = FirstThrottleTestView()

        for throttle_class in (
            UserBurstRateThrottle,
            UserSustainedRateThrottle,
        ):
            with self.subTest(
                throttle_class=throttle_class,
            ):
                self.assertIsNone(
                    throttle_class().get_cache_key(
                        request,
                        view,
                    )
                )

    def test_user_throttles_use_public_user_identifier(
        self,
    ) -> None:
        public_id = uuid4()
        request = self.factory.get(
            '/api/v1/resource/',
        )
        request.user = SimpleNamespace(
            is_authenticated=True,
            public_id=public_id,
        )
        view = FirstThrottleTestView()

        burst_key = UserBurstRateThrottle().get_cache_key(
            request,
            view,
        )
        sustained_key = UserSustainedRateThrottle().get_cache_key(
            request,
            view,
        )

        self.assertIsNotNone(burst_key)
        self.assertIsNotNone(sustained_key)
        self.assertIn(
            str(public_id),
            burst_key,
        )
        self.assertIn(
            str(public_id),
            sustained_key,
        )
        self.assertNotEqual(
            burst_key,
            sustained_key,
        )

    def test_global_throttles_are_configured(
        self,
    ) -> None:
        self.assertEqual(
            APIView.throttle_classes,
            [
                AnonymousBurstRateThrottle,
                AnonymousSustainedRateThrottle,
                UserBurstRateThrottle,
                UserSustainedRateThrottle,
            ],
        )


class TwoRequestAnonymousThrottle(
    AnonymousBurstRateThrottle,
):
    rate = '2/min'


class ThrottledTestView(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = [
        TwoRequestAnonymousThrottle,
    ]

    def get(self, request: Request) -> Response:
        return Response(
            {
                'allowed': True,
            }
        )


urlpatterns = [
    url_path(
        'throttled/',
        ThrottledTestView.as_view(),
        name='throttled-test',
    ),
]


@override_settings(ROOT_URLCONF=__name__)
class ThrottledResponseTests(APITestCase):
    endpoint = '/throttled/'

    cache_key = (
        TwoRequestAnonymousThrottle.cache_format
        % {
            'scope': TwoRequestAnonymousThrottle.scope,
            'ident': '127.0.0.1',
        }
        + ':throttled-test'
    )

    def setUp(self) -> None:
        cache.delete(self.cache_key)

    def tearDown(self) -> None:
        cache.delete(self.cache_key)

    def test_returns_standard_throttled_response(
        self,
    ) -> None:
        first_response = self.client.get(
            self.endpoint,
        )
        second_response = self.client.get(
            self.endpoint,
        )
        response = self.client.get(
            self.endpoint,
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            second_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS,
        )

        body = response.json()

        self.assertEqual(
            body['error']['type'],
            'urn:augustinian-path:problem:throttled',
        )
        self.assertEqual(
            body['error']['status'],
            status.HTTP_429_TOO_MANY_REQUESTS,
        )
        self.assertEqual(
            body['error']['instance'],
            self.endpoint,
        )
        self.assertEqual(
            body['meta']['api_version'],
            'v1',
        )
        self.assertIn(
            'Retry-After',
            response.headers,
        )

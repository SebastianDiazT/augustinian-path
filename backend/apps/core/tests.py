from rest_framework import status
from rest_framework.test import APITestCase


class HealthEndpointTests(APITestCase):
    endpoint = '/api/v1/health/'

    def test_health_endpoint_returns_service_status(self) -> None:
        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                'status': 'ok',
                'service': 'ruta-unsa-backend',
                'version': 'v1',
            },
        )

from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

class TestCoreAPI:
    def test_health_check_returns_ok_when_database_is_connected(self):
        client = APIClient()
        res = client.get(reverse('core:health'))

        assert res.status_code == 200
        assert res.data['status'] == 'ok'
        assert res.data['database'] == 'ok'

    @patch('apps.core.views.connection.ensure_connection')
    def test_health_check_returns_degraded_when_database_is_down(self, mock_conn):
        mock_conn.side_effect = Exception('Conexión rechazada')

        client = APIClient()
        res = client.get(reverse('core:health'))

        assert res.status_code == 503
        assert res.data['status'] == 'degraded'
        assert res.data['database'] == 'unreachable'

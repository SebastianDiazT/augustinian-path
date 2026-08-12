from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404

from apps.core.exceptions import _message_for, custom_exception_handler


class TestCoreExceptions:
    def test_django_validation_error_is_handled_gracefully(self):
        exc = DjangoValidationError({'campo': ['Dato inválido']})
        res = custom_exception_handler(exc, {})

        assert res is not None
        assert res.status_code == 400
        assert res.data['error']['code'] == 'VALIDATION_ERROR'
        assert res.data['error']['details'][0]['field'] == 'campo'

    def test_message_for_prevents_index_error_on_empty_lists(self):
        detail = {'campo': []}
        message = _message_for('ERROR', detail)
        assert message == '[]'

        assert _message_for('VALIDATION_ERROR', {'c': ['msg']}) == 'Error de validación.'
        assert _message_for('ERROR', {'c': ['msg']}) == 'msg'

    def test_standard_exceptions_are_formatted(self):
        res_404 = custom_exception_handler(Http404('No existe'), {})
        assert res_404.status_code == 404
        assert res_404.data['error']['code'] == 'NOT_FOUND'

        res_403 = custom_exception_handler(DjangoPermissionDenied('Denegado'), {})
        assert res_403.status_code == 403
        assert res_403.data['error']['code'] == 'PERMISSION_DENIED'

    def test_unhandled_exception_returns_500(self):
        exc = ValueError('Error crítico inesperado')
        res = custom_exception_handler(exc, {})
        assert res.status_code == 500
        assert res.data['error']['code'] == 'INTERNAL_ERROR'

    def test_code_for_conflict_and_details_formatting(self):
        from rest_framework.exceptions import APIException

        from apps.core.exceptions import _code_for, _details_from, _message_for
        class ConflictException(APIException):
            status_code = 409

        assert _code_for(ConflictException('x')) == 'CONFLICT'

        details = _details_from(['Error 1', 'Error 2'])
        assert details[0]['message'] == 'Error 1'
        assert details[0]['field'] is None

        assert _message_for('UNKNOWN_CODE', None) == 'Ocurrió un error procesando la solicitud.'
        assert _message_for('ERR', 'Cadena de texto pura') == 'Cadena de texto pura'

    def test_generic_exception_code_and_message_fallback(self):
        from apps.core.exceptions import _code_for, _message_for

        assert _code_for(Exception('Error nativo')) == 'ERROR'

        assert _message_for('ERROR', None) == 'Ocurrió un error procesando la solicitud.'
        assert _message_for('ERROR', {}) == 'Ocurrió un error procesando la solicitud.'
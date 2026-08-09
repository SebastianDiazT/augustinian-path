from .context import get_request_id


def build_error_payload(code: str, message: str, details=None) -> dict:
    return {
        'error': {
            'code': code,
            'message': message,
            'details': details or [],
            'request_id': get_request_id(),
        }
    }

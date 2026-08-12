from rest_framework import status
from rest_framework.exceptions import APIException


class ConflictError(APIException):
    """409 — for conditional updates that didn't find the expected state
    (e.g. a MembershipRequest someone else already resolved). `core`'s
    exception handler maps this to the 'CONFLICT' code in the global
    error contract."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = 'El recurso ya fue modificado por otra solicitud.'
    default_code = 'conflict'

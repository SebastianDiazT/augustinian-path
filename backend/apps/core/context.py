from contextvars import ContextVar

_request_id_ctx_var: ContextVar[str | None] = ContextVar('request_id', default=None)


def get_request_id() -> str | None:
    """Devuelve el request id del request actual, o None si no hay ninguno seteado."""
    return _request_id_ctx_var.get()


def set_request_id(request_id: str):
    """Setea el request id del request actual. Devuelve un token para poder resetear."""
    return _request_id_ctx_var.set(request_id)


def reset_request_id(token) -> None:
    """Restaura el valor previo del contextvar, usando el token de `set_request_id`."""
    _request_id_ctx_var.reset(token)

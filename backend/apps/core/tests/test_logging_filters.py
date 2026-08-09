import logging

from apps.core.context import reset_request_id, set_request_id
from apps.core.logging_filters import RequestIdLogFilter


def _make_record():
    return logging.LogRecord(
        name='test',
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg='mensaje de prueba',
        args=None,
        exc_info=None,
    )


def test_filter_injects_current_request_id():
    token = set_request_id('abc-123')
    try:
        record = _make_record()
        assert RequestIdLogFilter().filter(record) is True
        assert record.request_id == 'abc-123'
    finally:
        reset_request_id(token)


def test_filter_defaults_to_dash_outside_a_request():
    record = _make_record()
    assert RequestIdLogFilter().filter(record) is True
    assert record.request_id == '-'

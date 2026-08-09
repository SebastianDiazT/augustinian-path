from rest_framework.renderers import JSONRenderer

from .context import get_request_id


class EnvelopeJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if data is not None and isinstance(data, dict):
            is_error_envelope = 'error' in data and isinstance(data['error'], dict)
            is_already_wrapped = 'data' in data and 'meta' in data
            if not is_error_envelope and not is_already_wrapped:
                data = {'data': data, 'meta': {'request_id': get_request_id()}}
        elif data is not None and not isinstance(data, dict):
            data = {'data': data, 'meta': {'request_id': get_request_id()}}

        return super().render(data, accepted_media_type, renderer_context)

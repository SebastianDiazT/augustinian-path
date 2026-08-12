from rest_framework.renderers import JSONRenderer

from .context import get_request_id

_ENVELOPE_KEYS = ({'data', 'meta'}, {'error'})


class EnvelopeJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        already_wrapped = isinstance(data, dict) and set(data.keys()) in _ENVELOPE_KEYS
        if data is None or already_wrapped:
            return super().render(data, accepted_media_type, renderer_context)

        wrapped = {'data': data, 'meta': {'request_id': get_request_id()}}
        return super().render(wrapped, accepted_media_type, renderer_context)

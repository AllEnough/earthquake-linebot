import os, sys, types
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from linebot.v3.messaging.models import TextMessage, ImageMessage, PushMessageRequest

dummy_config = types.ModuleType("config")
dummy_config.configuration = object()
class DummyCollection:
    def find(self, *args, **kwargs):
        return []
dummy_config.collection = DummyCollection()
sys.modules['config'] = dummy_config

import line_push_utils


def test_push_image_to_all_users(monkeypatch):
    calls = []

    class DummyMessagingApi:
        def __init__(self, api_client):
            pass
        def push_message(self, request):
            calls.append(request)

    class DummyApiClient:
        def __init__(self, config):
            pass
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            pass

    class DummyCollection:
        def find(self, *args, **kwargs):
            return [{'user_id': 'U1'}, {'user_id': 'U2'}]

    monkeypatch.setattr(line_push_utils, 'MessagingApi', DummyMessagingApi)
    monkeypatch.setattr(line_push_utils, 'ApiClient', DummyApiClient)
    monkeypatch.setattr(line_push_utils, 'collection', DummyCollection())

    line_push_utils.push_image_to_all_users('https://example.com/img.png', 'alt')

    assert len(calls) == 2
    for req in calls:
        assert isinstance(req, PushMessageRequest)
        assert req.messages[0].text == 'alt'
        assert isinstance(req.messages[1], ImageMessage)
        assert req.messages[1].original_content_url == 'https://example.com/img.png'

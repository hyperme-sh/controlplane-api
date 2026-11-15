import importlib.util
import json
from pathlib import Path
import sys
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import inventory_registry as registry
import verify_history_review as history


def test_registry_pagination_cannot_escape():
    for url in ['https://evil.invalid/v2/hyperme-sh/controlplane-api/runtime/tags/list','https://ghcr.io/v2/other/runtime/tags/list','https://ghcr.io/v2/hyperme-sh/controlplane-api/runtime/../other']:
        with pytest.raises(ValueError):registry.registry_url(url)


def test_authorized_empty_inventory_is_distinct_from_request_failure():
    result=registry.inventory(lambda url:({'tags':[]},{},b''))
    assert result['images']==[]
    def denied(url):raise PermissionError('denied')
    with pytest.raises(PermissionError):registry.inventory(denied)


def test_registry_manifest_digest_must_match():
    def request(url):
        if '/tags/' in url:return {'tags':['test']},{},b''
        return {},{'Docker-Content-Digest':'sha256:'+'a'*64},b'{}'
    with pytest.raises(ValueError,match='manifest bytes'):registry.inventory(request)


def test_new_historical_coordinate_refuses():
    with pytest.raises(ValueError,match='inventory'):
        history.verify({'history_findings':[{'object':'a','path':'b'}]},{'publication_cleared':False,'findings':[]})


def test_changed_historical_bytes_refuse(monkeypatch):
    r={'object':'a','path':'b','blob_sha256':'0'*64,'content_sha256':'0'*64,'classification':'legacy-provider-settings'}
    monkeypatch.setattr(history.subprocess,'check_output',lambda *a:b'changed')
    with pytest.raises(ValueError,match='blob'):
        history.verify({'history_findings':[r]},{'publication_cleared':False,'findings':[r]})

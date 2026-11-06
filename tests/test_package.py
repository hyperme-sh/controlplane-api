import importlib.util
from importlib.metadata import requires
import pkgutil
import importlib
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from controlplane_api import health, version


def test_all_public_modules_import_without_legacy_services():
    import controlplane_api
    for module in pkgutil.walk_packages(controlplane_api.__path__, controlplane_api.__name__ + '.'):
        importlib.import_module(module.name)
    for name in ('api', 'hypermesh_service', 'user_service', 'aiuditor_service'):
        assert importlib.util.find_spec(name) is None


@pytest.mark.parametrize('name,sha', [
    ('controlplane-identity', '5aeff3d2c00568f39ca6e8b75c7e63883d3a510b'),
    ('controlplane-events', '76750a7c620950c8d0b911664ef4e605bc4d9188'),
])
def test_dependency_metadata(name, sha):
    dep, = [d for d in requires('controlplane-api') if d.startswith(name + ' ')]
    assert dep == f'{name} @ git+https://github.com/hyperme-sh/{name}.git@{sha}'


def test_identity_uses_shared_settings(monkeypatch):
    from controlplane_api.config import settings
    from controlplane_identity.configuration import settings as identity
    monkeypatch.setattr(settings, 'api_key_exchange_jwt_secret', 'package-test-secret')
    assert identity.usable_api_key_exchange_secret() == settings.usable_api_key_exchange_secret()


def test_plain_health_and_version_http(monkeypatch):
    for key in ('CPEDGE_HYPERMESH_SERVICE_URL', 'GIT_SHA', 'SOURCE_SHA', 'HYPERMESH_SOURCE_SHA', 'BUILT_AT', 'SPANOPTICON_IMAGE_DIGEST', 'IMAGE_DIGEST'):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv('SERVICE_NAME', 'api-wheel-test')
    app = FastAPI()
    app.include_router(health.router, prefix='/api/v1')
    app.include_router(version.router)
    with TestClient(app) as client:
        assert client.get('/api/v1/health/').json() == {'status': 'Ok'}
        assert client.get('/version').json() == {'service': 'api-wheel-test', 'git_sha': 'unknown', 'built_at': 'unknown'}


@pytest.mark.parametrize('reachable,status', [(True, 200), (False, 503)])
def test_catalog_health_controls_http_status(monkeypatch, reachable, status):
    monkeypatch.setenv('CPEDGE_HYPERMESH_SERVICE_URL', 'https://catalog.invalid')
    seen = []
    def probe(url):
        seen.append(url)
        return reachable
    monkeypatch.setattr(health, 'hypermesh_catalog_reachable', probe)
    app = FastAPI()
    app.include_router(health.router)
    with TestClient(app) as client:
        response = client.get('/health/')
    assert response.status_code == status
    assert seen == ['https://catalog.invalid']


def test_catalog_network_failure_is_unhealthy(monkeypatch):
    import urllib.error
    def fail(*args, **kwargs):
        raise urllib.error.URLError('offline')
    monkeypatch.setattr(health.urllib.request, 'urlopen', fail)
    assert health.hypermesh_catalog_reachable('https://catalog.invalid') is False


def test_version_filters_secrets_and_uses_valid_fallback():
    sha = 'a' * 40
    assert version.version_payload({'SERVICE_NAME': 'Example', 'GIT_SHA': 'bad', 'SOURCE_SHA': sha,
        'BUILT_AT': '2026-11-02T00:00:00Z', 'JWT_SECRET': 'never-output'}) == {
        'service': 'example', 'git_sha': sha, 'built_at': '2026-11-02T00:00:00Z'}


def test_events_dependency_and_metrics_load():
    from controlplane_api import metrics
    from controlplane_events.store import delivery_counts_sync
    from sqlalchemy import create_engine, text
    assert metrics.HTTP_REQUESTS is not None
    engine = create_engine('sqlite://')
    try:
        with engine.connect() as connection:
            connection.execute(text('CREATE TABLE controlplane_event_deliveries (status TEXT)'))
            assert delivery_counts_sync(connection) == (0, 0)
    finally:
        engine.dispose()

# controlplane-api

`controlplane-api` (import name `controlplane_api`) is the shared HTTP and process scaffolding for Hypermesh control-plane services. One Python process uses it for settings, logging, exceptions, health and version routes, browser CORS, permission names, operator-plugin registration, shared DTOs, event-type names, and Prometheus metrics.

## Why

Control-plane services (the public edge, the Hypermesh service, auth, payments, and the other core APIs) need the same process setup and the same external shapes. Health and version payloads, permission strings, event-type names, and metric series have to match across those processes so a load balancer, a scraper, and an operator console can treat them uniformly.

Putting that scaffolding in one library keeps each service from reimplementing settings binding, the Prometheus registry, and the operator plugin list. Product code, including the Hypermesh lease handlers, stays in the services that own those routes. This package supplies the shared pieces those services call.

## How it works

Importing `controlplane_api.config` builds one `Settings` object for the process and passes it to `controlplane_identity.configuration.configure_identity`. Identity checks (Keycloak JWT validation, API-key exchange, internal tokens) then read that same object. The process also owns one Prometheus registry and one in-memory operator plugin list. Lookups return copies, so a caller cannot rewrite a registered declaration through the object it received.

| Module | Role |
|---|---|
| `controlplane_api.config` | Environment-backed `Settings`, including Keycloak, service URLs, and internal tokens. Binds the identity library. |
| `controlplane_api.logging` | Console logging for the `uvicorn`, `api`, and `databases` loggers. |
| `controlplane_api.exceptions` | Shared API exception types (`NotFoundException`, `ConflictException`, `ForbiddenException`, and others). |
| `controlplane_api.utils` | Tenancy helpers, password checks, email links, and a JSONL audit writer under the system temp directory. |
| `controlplane_api.event_types` | Versioned `event_type` strings. Transport lives in `controlplane-events`. |
| `controlplane_api.health` | `GET /health/` scaffold. |
| `controlplane_api.version` | Unauthenticated `GET /version` build identity. |
| `controlplane_api.service_cors` | Optional browser CORS middleware. |
| `controlplane_api.permissions` | Permission claim names, including host and operator claims. |
| `controlplane_api.operator.plugins` | Process-local registration of trusted operator plugin declarations. |
| `controlplane_api.metrics` | RED HTTP metrics, Hypermesh lease and host series, and a separate `/metrics` server. |
| `controlplane_api.dtos` | `HealthCheckResponseDto` and audit log models. |

`Settings` loads `.env` and the process environment (pydantic-settings). Empty strings for Keycloak URLs fall back to a local realm at `http://localhost:8081/realms/controlplane`. Shared secrets that match a published development default are treated as unset, so API-key exchange and the api-keys internal token fail closed until a deployment sets its own values.

Operator claims (`operator:console`, `operator:support`, `operator:program`, `operator:resolve`, `org:manage`, `org:own`) are explicit permission strings. `register_plugin` accepts a declaration from trusted code in this process, requires `id`, `title`, `kind` (`builtin` or `slot`), and `permission`, and rejects a duplicate id.

HTTP metrics use the matched route template. `GET /metrics` is a separate threaded server (`METRICS_PORT`, default `9100`), not a route on the public app. `METRICS_ENABLED=0` skips the bind. `METRICS_ADDR=compose` binds the compose-network address and skips loopback, tunnel, and WireGuard addresses (`HYPERMESH_WG_GATEWAY_ADDR`, default `10.77.0.1/24`).

## Practical use

The package on this line is **0.23.0** and requires **Python 3.13+**. [uv](https://docs.astral.sh/uv/) **0.11.26** matches CI. Two dependencies are pinned by full commit in `pyproject.toml` and `uv.lock`:

| Package | Repository | Commit |
|---|---|---|
| `controlplane-identity` | [hyperme-sh/controlplane-identity](https://github.com/hyperme-sh/controlplane-identity) | `5aeff3d2c00568f39ca6e8b75c7e63883d3a510b` |
| `controlplane-events` | [hyperme-sh/controlplane-events](https://github.com/hyperme-sh/controlplane-events) | `2a49f9af5f6c4dc9d6c4ddebc83c41d6331e2c87` |

The coordinated test bundle [`0.24.0-test.1`](https://github.com/hyperme-sh/controlplane-api/releases/tag/0.24.0-test.1) is this package at revision `732256a5207ee502d7bf70cb171cf2eea1803b87` and ships `controlplane_api-0.23.0`. The stable tag [`v0.24.0`](https://github.com/hyperme-sh/controlplane-api/releases/tag/v0.24.0) is an earlier published build whose wheel is `controlplane_api-0.24.0`. Channel rules are in [docs/releasing.md](docs/releasing.md).

Clone and install the locked development environment:

```sh
git clone https://github.com/hyperme-sh/controlplane-api.git
cd controlplane-api
uv sync --frozen
```

From another project, pin the same revision:

```sh
uv add "controlplane-api @ git+https://github.com/hyperme-sh/controlplane-api.git@732256a5207ee502d7bf70cb171cf2eea1803b87"
```

That install also fetches the identity and events commits above. A minimal FastAPI process mounts health under `/api/v1` and version at the application root:

```python
import os

from fastapi import FastAPI

from controlplane_api.health import router as health_router
from controlplane_api.logging import configure_logging
from controlplane_api.metrics import install_http_metrics
from controlplane_api.service_cors import add_optional_service_cors
from controlplane_api.version import router as version_router

os.environ.setdefault("SERVICE_NAME", "example-control-plane")
os.environ.setdefault("METRICS_ENABLED", "0")

configure_logging()
app = FastAPI(title="example-control-plane")
app.include_router(health_router, prefix="/api/v1")
app.include_router(version_router)
install_http_metrics(app, service="example-control-plane")
add_optional_service_cors(app, env_var="EXAMPLE_CORS_ORIGINS")
```

Save that module as `app.py` next to a checkout of this repository (or on `PYTHONPATH` after the `uv add` above). From the clone:

```sh
export SERVICE_NAME=example-control-plane
export GIT_SHA=732256a5207ee502d7bf70cb171cf2eea1803b87
export BUILT_AT=2026-11-05T19:22:28Z
export METRICS_ENABLED=0
uv run python -c '
from fastapi.testclient import TestClient
import app
client = TestClient(app.app)
print(client.get("/api/v1/health/").json())
print(client.get("/version").json())
'
```

`GET /api/v1/health/` returns `{"status":"Ok"}` when `CPEDGE_HYPERMESH_SERVICE_URL` is unset. `GET /version` returns `service`, `git_sha`, and `built_at`. `GIT_SHA` must be 40 hex characters or the field is `unknown`. `BUILT_AT` must be UTC `YYYY-MM-DDTHH:MM:SSZ`. A `sha256:` image digest in `SPANOPTICON_IMAGE_DIGEST` or `IMAGE_DIGEST` is added as `image_digest`. Tokens and database URLs are not part of the payload.

Set production credentials in the environment before serving real traffic. The fields that matter first are `DATABASE_URL`, `KEYCLOAK_JWKS_URL`, `KEYCLOAK_ISSUER`, `KEYCLOAK_ALLOWED_CLIENT_IDS`, `JWT_SECRET`, `REFRESH_TOKEN_SECRET`, `API_KEY_EXCHANGE_JWT_SECRET`, and `API_KEYS_INTERNAL_TOKEN`. `SERVICE_NAME` is the name in event envelopes and on `/version` (for example `gateway` or `user-service`).

To serve `GET /metrics`, leave `METRICS_ENABLED` unset and call `start_metrics_server()` from `controlplane_api.metrics` during startup. The default listen address is `0.0.0.0:9100`.

Trusted in-process code can add an operator plugin:

```python
from controlplane_api.operator.plugins import plugin_by_id, register_plugin

register_plugin({
    "id": "example.local",
    "title": "Example",
    "kind": "builtin",
    "permission": "operator:support",
    "reads": ["/example"],
    "actions": ["inspect"],
})
assert plugin_by_id("example.local")["actions"] == ["inspect"]
```

Event names used on the bus are constants, for example `PAYMENT_SUCCEEDED_V1` (`payment.succeeded.v1`) and `LISTING_CREATED_V1` (`listing.created.v1`) in `controlplane_api.event_types`.

## How Hypermesh uses it

Host agents and the visor talk to the control plane over HTTP. Each control-plane Python service links this library into its process. The Hypermesh service, the public edge, auth, and payment-service then call the pieces below as leases, listings, and payouts move.

**Public edge and the catalog.** Services include `health.router` (the edge uses the `/api/v1` prefix, so the public probe is `GET /api/v1/health/`). The edge sets `CPEDGE_HYPERMESH_SERVICE_URL`. The health handler then sends `GET {that url}/api/v1/hypermesh/catalog` with a 2 second timeout. Catalog HTTP 200 keeps this route at 200 and `{"status":"Ok"}`. A connection failure, timeout, or any other status returns HTTP 503 and `{"status":"hypermesh unreachable"}`. The test-plane load balancer treats 200 on this route as the public health signal, so a down Hypermesh catalog takes the edge out of service. Processes that leave `CPEDGE_HYPERMESH_SERVICE_URL` unset skip the probe.

**Host heartbeats.** Enrolled hosts heartbeat the Hypermesh service every 30 seconds and pull jobs under `/api/v1/hypermesh/agent/`. The fleet-health loop publishes those timestamps with `publish_heartbeat_snapshot`: a map of device id to `(last_heartbeat_unix, stale_after_seconds)`. The scrape exports `hypermesh_host_heartbeat_age_seconds{device_id}` and `hypermesh_hosts_fresh` (hosts still inside the stale window). Age is computed when Prometheus scrapes. Device ids that are not UUIDs are dropped. Clearing the snapshot omits the series.

**Renter host selection.** A request that enters host selection calls `begin_host_selection`. The handler may name an outcome with `note_host_selection`. `finish_host_selection(status_code)` increments `hypermesh_host_selection_total` once. Named outcomes are `success`, `grace_wait`, `transient_503`, and `conflict_409`. When the handler has not named one, a status below 300 counts as `success`, 503 as `transient_503`, and 409 as `conflict_409`.

**Lease lifecycle.** After the control plane creates, starts, ends, or fails a lease, it calls `record_lease(event, reason)`. The series is `hypermesh_leases_total{event,reason}`. Events are `created`, `started`, `ended`, and `failed`. Reasons stay on a fixed set: `schedule_hold`, `not_green` (the host is not eligible for placement), `recorded_host_failure`, `cert_failed` (host certification failed before the window ended), `compact_cert_failed`, `path_b_failed` (lab soak on the AGX bench), `instance_check_failed`, `lease_stop_failed`, `deenroll`, `violation`, and `other`. The host agent still runs `lease_start`, `lease_stop`, `lease_cancel`, and `lease_expiry` jobs. This counter is the control plane's record of those transitions.

**Listings a renter reads.** The Hypermesh in-process listing cache registers itself with `export_read_cache_samples`. Scrapes then export `hypermesh_read_cache_hits_total`, `hypermesh_read_cache_misses_total`, and `hypermesh_read_cache_invalidations_total` for the scopes `nodes`, `hosts`, `catalog`, and `classes`. The cache implementation stays in the Hypermesh service. This package keeps the registered object and reads `samples()` at scrape time. With no cache registered, those series are absent.

**Pricing rounds.** The control plane calls the separate [hypermesh-pricing](https://github.com/hyperme-sh/hypermesh-pricing) engine, then `record_pricing_round`. A failed round increments `hypermesh_pricing_rounds_total{result="failure"}`. A round that persisted increments `result="run"` and sets `hypermesh_pricing_round_last_success_timestamp_seconds`.

**Payment and host binding.** `HYPERMESH_INTERNAL_TOKEN` is the internal credential for Hypermesh `POST /internal/payment-succeeded` and for complete and payout routes that accept either an owner session or this token. `PAYMENT_INTERNAL_TOKEN` is the matching credential toward payment-service. In production the Hypermesh service consumes `payment.succeeded.v1` from the event bus (the Postgres events table, or Azure Service Bus when `AZURE_SERVICE_BUS_CONNECTION_STRING` is set). The string constant for that event is `PAYMENT_SUCCEEDED_V1`. `auth_host_binding_url` is the Hypermesh owner URL auth uses to resolve a host identity, with `host_binding_internal_token` (at least 32 characters). `hypermesh_url` defaults to `http://127.0.0.1:8010`.

**Operator console.** Built-in declarations in `controlplane_api.config.operator_plugins` name the Hypermesh plugins the console may call. They are not the HTTP handlers.

| Id | Reads | Actions | Permission |
|---|---|---|---|
| `hypermesh.hosts` | `/api/v1/hypermesh/devices` | `sell_pause`, `schedule_hold`, `schedule_restore`, `deenroll`, `enroll_token` | `operator:support` |
| `hypermesh.models` | model configuration, `/api/v1/hypermesh/catalog`, AIuditor suite and envelopes | `suite_edit` | `operator:support` |
| `hypermesh.aiuditor` | AIuditor meta, connections, violations, suite | `violation_create`, `approval_resolve`, `suite_edit` | `operator:support` |
| `hypermesh.aimmune` | auditor ticket and grant URLs | `ticket_resolve`, `grant_resolve`, `grant_revoke` | `operator:resolve` |

`schedule_hold` and `schedule_restore` are resolve actions on `hypermesh.hosts`. `host:manage_tenants` is a separate permission for host tenant administration.

**Visor and CLI.** The default `KEYCLOAK_ALLOWED_CLIENT_IDS` includes `hypermesh-native`. A deployment that sets the variable without that id drops the visor and CLI client. Interactive human tokens for that client are checked by the identity library bound to this process's `Settings`, including the age-confirmation timestamp on the pinned identity commit. Service-account tokens skip that check.

**Build identity on every service.** `GET /version` and the `build_info` gauge report the image that is running. `GIT_SHA` is the commit baked into the image. `SOURCE_SHA` and `HYPERMESH_SOURCE_SHA` cover images that only baked the Hypermesh source commit. Retagging an image does not change those values.

**Gateway smoke.** `HYPERMESH_SMOKE_OIDC` is the environment flag for the smoke identity. The session route defaults to `/hypermesh-smoke/session`, and the session marker claim defaults to `hypermesh_smoke`, which has to stay off the reserved JWT claim set.

## Develop and test

```sh
uv sync --frozen
bash scripts/check-package.sh
```

`scripts/check-package.sh` checks `uv.lock`, builds a wheel and sdist, runs the test suite from the source tree, from that wheel installed outside the checkout, and from a wheel rebuilt from the sdist. The two wheels must carry the same runtime sources, and their exported release contracts must match.

Pull requests run the same script with `--fixtures`. That path installs the checked-in wheels in `tests_artifacts/dependencies` for `controlplane-identity` and `controlplane-events`. Main validation resolves those pinned commits from Git. See [docs/releasing.md](docs/releasing.md) for qualification artifacts, test bundles, and stable tags.

## Release and versioning

The version in `pyproject.toml` is **0.23.0**. GitHub release [v0.24.0](https://github.com/hyperme-sh/controlplane-api/releases/tag/v0.24.0) is the immutable stable distribution recorded under `releases/accepted/`. Successful validation of `main` can publish a `0.24.0-test.N` prerelease bundle; the files inside that bundle keep the package version of the build (`0.23.0` today). A stable release is a separate `v*` tag.

Channel behavior, the `test-<commit>` snapshots, and the stable tag workflow are documented in [docs/releasing.md](docs/releasing.md). Admission steps for a candidate bundle are in [docs/release-policy.md](docs/release-policy.md).

## License

This package is licensed under [Apache-2.0](LICENSE). Dependencies keep their own licenses.

### Health metadata compatibility

The health DTO uses Pydantic's `json_schema_extra` while retaining its complete
JSON Schema, OpenAPI example and HTTP payload. The test environment uses
`httpx2` for Starlette's TestClient; runtime dependency declarations and package
version remain unchanged.

`compatibility/health-field-metadata.json` records the exact previous successful
main artifact, contract and installer hashes, plus the one reviewed health-module
transition. Qualification keeps the complete byte exporter and historical
records intact. `scripts/qualify_health_metadata.py` rejects every other runtime,
inventory or installer change, binds a fresh candidate descriptor to the actual
built wheel, and runs the unchanged candidate verifier. Its compatibility receipt
is retained with the three package test inventories. This is development
qualification, not a stable baseline, publication or deployment authorization.

The implementation follows [Pydantic's field schema customization](https://docs.pydantic.dev/latest/concepts/json_schema/)
and [Starlette's TestClient dependency contract](https://starlette.dev/testclient/).

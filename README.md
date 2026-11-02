# controlplane-api

Shared configuration and HTTP scaffolding: settings, logging, exceptions,
utilities, event names, metrics, CORS, health/version endpoints, permissions,
operator plugin registration and DTOs. Package version is **0.23.0**.

The process owns one settings instance, Prometheus registry and router set.
Settings configure the identity library. Plugin registration accepts trusted
local declarations, rejects duplicate IDs and returns independent copies.
The package imports no legacy API or product implementation.

## Development

Use Python 3.13+ and uv 0.11.26. Read access over HTTPS is required for the private
`hyperme-sh/controlplane-identity` and `hyperme-sh/controlplane-events` repositories.
Both dependencies use full immutable commit pins in distribution metadata and
uv.lock, so normal wheel installers resolve the same revisions.

```sh
uv sync --frozen
bash scripts/check-package.sh
```

Tests run from source, a fresh wheel outside the checkout and a wheel rebuilt
from the source archive. Both wheel payloads must match every runtime source file.
Consumer compatibility aliases and full service suites require their own checks.

## CI

The main-push/manual workflow uses GitHub-hosted Ubuntu workers, pinned actions,
read-only contents and checkout without persisted credentials. It requires
`DEPENDENCY_READ_TOKEN` with contents:read on the identity and events repositories
only; Git authentication headers are restricted to those repository URLs.
The job rejects non-main refs and does not run on pull-request events.
Actions remains disabled until scoped dependency access and the hosted-worker
policy are configured and a main run succeeds. No publishing or deployment is
performed by this workflow.

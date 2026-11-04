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

The main-push/manual workflow uses the shared-local self-hosted Linux runners, pinned actions,
read-only contents and checkout without persisted credentials. It requires
`DEPENDENCY_READ_TOKEN` with contents:read on the identity and events repositories
only; Git authentication headers are restricted to those repository URLs.
The job rejects non-main refs and does not run on pull-request events.
Actions remains disabled until scoped dependency access and the hosted-worker
policy are configured and a main run succeeds. No publishing or deployment is
performed by this workflow.

## Release channels

Successful main-push validation retains the validated Python wheel and source distribution and publishes
an immutable `test-<commit>` GitHub prerelease. Push a `vMAJOR.MINOR.PATCH`
tag at that tested commit to promote the exact files to a stable release,
without rebuilding. Repository visibility applies to all package assets.
Package metadata versions are preserved; these are GitHub distribution snapshots,
not automatic PyPI publication or service deployment.

Promotion requires the original Actions artifact (90-day requested retention;
organization policy may shorten it). Expired evidence fails closed: validate a
new main revision. The publisher verifies the run, source, workflow and artifact
digest independently of release metadata. Repository immutable releases must be
enabled. See the [shared release contract](https://github.com/hyperme-sh/.github/blob/7749591fccd30d46ba9b0adabe82114001c9d0de/actions/release-channel/README.md).

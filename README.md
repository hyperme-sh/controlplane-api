# controlplane-api

Shared configuration and HTTP scaffolding: settings, logging, exceptions,
utilities, event names, metrics, CORS, health/version endpoints, permissions,
operator plugin registration and DTOs. Package version is **0.24.1**.

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
The main lane retains scoped dependency access. No deployment is performed by
this workflow.

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

### Immutable release candidate validation

The candidate job builds and uploads `tested-dist` immediately after the build, before running repository validators or tests. Source tests run in their own job. Only after they pass does a separate job
download that exact artifact ID and run fresh-wheel and rebuilt-sdist checks
against a disposable copy. Expected hashes remain in the invoking shell and
are rechecked after validation; neither downloaded nor staged distributions
may be replaced by tests. Tests cannot replace the
already uploaded candidate through a post-test staging step: validation never
uploads artifacts. The publisher requires the entire main-push workflow to
succeed and promotes only the immutable candidate. Failed validation leaves an
unpublished candidate, not a successful release. Both jobs keep the existing
shared-runner policy; this is artifact immutability, not host isolation.

To validate a previously built candidate locally, set `RELEASE_CANDIDATE_DIR` to
a directory containing exactly its wheel and source distribution when invoking
`scripts/check-package.sh`. With no candidate directory, the ordinary local
build-and-test path is unchanged.

## Isolated pull-request qualification

`bash scripts/check-package.sh --fixtures` uses real published dependency wheels
from `tests_artifacts/dependencies`, bound to the declared full Git revisions,
locked versions and SHA-256 digests. The fixtures are excluded from wheel and
source distributions. Missing/tampered artifacts or changed pins fail validation.
Frozen registry dependencies are installed normally; private dependencies use
the verified fixture bytes without resolving Git or receiving credentials.
The separate PR workflow runs on disposable Ubuntu workers with read-only
contents. The existing main workflow still resolves the actual private Git pins
and retains its scoped credential and runner boundaries.

Package CI exports complete runtime/resource contracts from actual wheels and
binds candidate digests to those builds. Rebuilt-sdist contracts must match.
Conservative byte comparisons reject implementation-only patch changes too;
semantic compatibility, installer metadata and deployed consumers remain distinct.

## Test qualification and stable acceptance

GitHub `test-<commit>` prereleases are development snapshots. Their embedded
package version does not reserve a stable version. Artifact and consumer evidence
lives under `releases/qualification`; the current wheel binding is still checked
by package CI, alongside any future explicit stable candidate. Earlier test
snapshot receipts are preserved there with an explicit non-stable classification.

`releases/accepted` and `SPANOPTICON_RELEASE_BASELINE_SHA` are reserved for an
actual immutable stable GitHub release. The pinned shared guard verifies the live
release channel, stable tag source and asset digests; a test snapshot cannot
become accepted through a provenance label. No stable baseline is recorded until
that release exists. Stable publication remains closed without a valid baseline;
first stable bootstrap and coordinated release qualification remain separate.
No stable version, approval prerequisite or deployment is introduced here.


### Published stable distribution

The accepted record binds the existing immutable `v0.24.0` release to its actual
GitHub release ID, source revision and published asset digests. Test snapshots
remain under `releases/qualification` and do not establish stable acceptance.
Runtime deployment and coordinated consumer acceptance remain separate.

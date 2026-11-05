# controlplane-api

## Current version authority

Current development version: `0.23.0`. The services remain before the unreleased
0.24.0 milestone. Earlier 0.24/1.0 preparation and publication notes below are
historical and do not authorize those versions. Existing tags and historical
artifacts remain untouched. Development uses exact source pins and rebuilt
artifacts; no prior release is required. Version changes, tags and publication
require the owner's explicit authorization to the agent.

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

Main validation retains its exact qualified files in Actions artifacts. It does
not create GitHub releases or tags. Historical `test-<commit>` prereleases remain
qualification evidence and do not establish an accepted stable release.

Stable publication requires an explicit `vMAJOR.MINOR.PATCH` tag, the exact
successful main validation artifact, compatible declared contracts and an actual
immutable stable baseline. The publisher independently verifies that evidence;
successful caller jobs alone cannot establish acceptance. Missing evidence and
first-stable bootstrap remain closed. Package qualification, coordinated consumer
acceptance and runtime deployment remain separate.

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
belongs under `releases/qualification`. Owning-package and artifact validation
remain separate from stable release admission. Future test receipts must carry
an explicit non-stable classification.

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

### Actions qualification and stable publication

Main merges and workflow completion do not publish GitHub test releases. Exact
qualification files remain in Actions artifacts with finite retention. The pinned
publisher independently verifies a real immutable stable baseline and refuses
qualification snapshots, even if a caller job reports success. Existing valid
stable records are retained; no release, version change, deployment or human
approval prerequisite is introduced by this correction.

## License

This package is licensed under [Apache-2.0](LICENSE). Dependencies retain their
own licenses; this declaration does not relicense bundled third-party material.

## Coordinated test bundles

This service opts into the `next: 0.24.0` train through
[.github/test-channel.json](.github/test-channel.json). Successful main validation
publishes its exact retained `tested-dist` files as immutable `0.24.0-test.N`
prerelease bundles. The pinned publisher verifies the run, source revision,
configuration and original Actions artifact digest without executing caller code
or receiving private dependency credentials. PRs validate without publication.

This test-channel authorization supersedes the older main-publication restriction
above. Package versions, dependency pins and accepted package baselines stay
unchanged; existing stable package admission remains separate. Coordinated
consumer/deployment selection must bind exact component commits and artifact
digests, not matching repository-local counters. No stable promotion is automatic.
Private jobs use debrunners and public jobs use hosted Ubuntu; no approval gates
are introduced. Missing original evidence or publication collisions fail closed.

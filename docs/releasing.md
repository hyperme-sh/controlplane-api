# Releasing controlplane-api

This page is the release-channel and qualification record for this repository. The README keeps only the version a caller should install. Admission steps for a candidate bundle are in [release-policy.md](release-policy.md). The Spanopticon manifest format and compatibility rules are in the [Spanopticon release policy](https://github.com/hyperme-sh/spanopticon/blob/main/docs/releases.md).

## Version recorded in source

`pyproject.toml` declares package version **0.23.0** and requires Python `>=3.13`. [`release-policy.json`](../release-policy.json) records line `0.23` and names `pyproject.toml` as the version file. The tag workflow passes that same line (`release-line: 0.23`) into admission.

The coordinated test channel in [`.github/test-channel.json`](../.github/test-channel.json) sets `"next": "0.24.0"`. That name is the bundle train. It does not rewrite the version field inside the wheel.

## Published stable release

GitHub release [v0.24.0](https://github.com/hyperme-sh/controlplane-api/releases/tag/v0.24.0) is the immutable stable distribution. [`releases/accepted/provenance.json`](../releases/accepted/provenance.json) binds it to release id `434687150`, source revision `6327a672c588fc16afb9656f2cacc89a91589858`, and these asset digests:

| Asset | SHA-256 |
|---|---|
| `controlplane_api-0.24.0-py3-none-any.whl` | `cc39416970f1808625ce53f11af22bc48b888dffdcecfed5d95e86a2d5f06349` |
| `controlplane_api-0.24.0.tar.gz` | `2c2edd00475e904c87f093ec81bc4d19b9c6a8d8af729c1ae44dd4cdcf440763` |
| `release-manifest.json` | `5f542beb0adb422d991f32ee786270c665e6ae10e3208ec412b7e19617ce9424` |

[`releases/accepted/release.json`](../releases/accepted/release.json) records that component on line `0.24` with version `0.24.0`. Current source is `0.23.0`. The `v0.24.0` tag remains the accepted historical build. Rebuilding `main` does not replace those assets.

`SPANOPTICON_RELEASE_BASELINE_SHA` is the repository variable set to the full commit of that accepted release. Admission compares a requested tag against that baseline.

## Main qualification

A push to `main` runs [`.github/workflows/package.yml`](../.github/workflows/package.yml) (Standalone package). The workflow:

1. Builds a wheel and sdist before executing tests and uploads those bytes as the `tested-dist` Actions artifact (90-day retention).
2. Resolves `controlplane-identity` and `controlplane-events` at the commits pinned in `pyproject.toml`. The job mints a contents:read token for those two repositories and attaches it only to those Git URLs.
3. Runs `bash scripts/check-package.sh` against the uploaded candidate. The script checks `uv.lock`, runs pytest from the source tree, installs the fresh wheel outside the checkout and runs pytest there, rebuilds a wheel from the sdist, and runs pytest again. `scripts/export_release_contract.py` writes the runtime contract from each wheel. The fresh-wheel contract and the rebuilt-sdist contract must be byte-identical. `scripts/verify_wheel.py` rejects a wheel whose runtime sources differ from the tree that built it.

That workflow reads repository contents and does not create a Git tag or a GitHub release. Exact qualification files stay in the Actions artifacts. Pull-request events do not run this workflow.

While this repository is public, the jobs select `ubuntu-24.04`. The workflow expression selects `[self-hosted, linux, x64, debrunner]` when the repository is private.

## Pull-request qualification

Pull requests run [`.github/workflows/consumer-qualification.yml`](../.github/workflows/consumer-qualification.yml), which executes:

```sh
bash scripts/check-package.sh --fixtures
```

`--fixtures` installs the wheels in [`tests_artifacts/dependencies`](../tests_artifacts/dependencies) after `scripts/verify_dependency_fixtures.py` checks them against [`manifest.json`](../tests_artifacts/dependencies/manifest.json). The manifest binds each wheel to the declared full Git revision, locked version, and SHA-256 digest. A missing file, a tampered wheel, or a pin that drifted from the manifest fails the run. Those wheels are test fixtures. The published wheel and sdist do not contain `tests_artifacts/`.

The pull-request job uses read-only contents and does not publish a release. Frozen third-party dependencies install from the lock. The identity and events packages come from the fixture bytes, so the job does not clone those repositories.

## Coordinated test bundles

After Standalone package succeeds on a `main` push, [`.github/workflows/test-bundles.yml`](../.github/workflows/test-bundles.yml) publishes one immutable prerelease named `0.24.0-test.N`. The pinned bundle publisher checks the workflow run, the source revision, the channel configuration, and the digest of the original `tested-dist` artifact. It publishes those retained files. It does not rebuild this repository in the publish job.

The bundle tag is the coordinated train name (`next` = `0.24.0`). The distributions inside keep the package version from the build. [`0.24.0-test.1`](https://github.com/hyperme-sh/controlplane-api/releases/tag/0.24.0-test.1) is revision `732256a5207ee502d7bf70cb171cf2eea1803b87` and contains:

| Asset | SHA-256 |
|---|---|
| `controlplane_api-0.23.0-py3-none-any.whl` | `99ba540637910a65cb4edc79ef45deb6abfd99a4c201eacf38346523b6d128d7` |
| `controlplane_api-0.23.0.tar.gz` | `6f3a020acb9229ae8a05bfb8f50cc7a72317814f8b1d47312df1dbba6c536623` |

A test bundle does not update `releases/accepted/` and does not move `v0.24.0`. Consumers that want a specific build bind the component commit and the artifact digest from `release-manifest.json` on that bundle. Pull requests do not publish bundles. A second publish that collides with an existing bundle fails.

## Development snapshots

Older GitHub prereleases named `test-<commit>` are development snapshots. The package version embedded in those files does not reserve a stable version number. Checked-in receipts live under [`releases/qualification/`](../releases/qualification). A snapshot tag is not an accepted stable release, including when a provenance file is attached. New test receipts carry an explicit non-stable classification.

## Stable publication

Pushing a `v*` tag runs [`.github/workflows/release.yml`](../.github/workflows/release.yml):

1. **Admission** calls the pinned Spanopticon workflow `component-release.yml` with `release-line` `0.23`, `baseline-ref` set from `SPANOPTICON_RELEASE_BASELINE_SHA`, and `requested-version` set from the tag.
2. **Publish** runs only after admission succeeds. It uses the pinned `release-channel` action, with `contents: write` and `actions: read`, to publish the already tested artifact for that tag. The publish job does not check out this repository or run its tests.

A green validation workflow is not by itself a stable release. The publisher checks the live release channel, the stable tag's source, and the asset digests. A `test-<commit>` snapshot or a `0.24.0-test.N` bundle cannot become the accepted release by relabeling. Changing a published artifact at the same version is rejected. Patch releases keep the accepted API contract.

Preparing the bundles admission reads is covered in [release-policy.md](release-policy.md): a real accepted record at `releases/accepted/release.json`, a candidate at `releases/candidate/release.json` generated from the release artifacts, and admission against the baseline. Missing baseline evidence fails closed. This repository's qualification workflows do not deploy a control plane.

## Dependency pins

Both Git dependencies are public repositories under `hyperme-sh` and are pinned by full commit in package metadata and `uv.lock`:

| Package | Commit |
|---|---|
| `controlplane-identity` | `5aeff3d2c00568f39ca6e8b75c7e63883d3a510b` |
| `controlplane-events` | `2a49f9af5f6c4dc9d6c4ddebc83c41d6331e2c87` |

The identity pin rejects an interactive human access token that has no age-confirmation timestamp (`terms_and_conditions`), including tokens whose authorized party is `hypermesh-native`. Machine and service-account tokens are unchanged. Importing `controlplane_api.config` applies that policy by passing this process's `Settings` instance to `configure_identity`. The fixture wheels under `tests_artifacts/dependencies` are built from those same revisions, and `scripts/check-package.sh` exercises the binding from source, from the fresh wheel, and from the rebuilt sdist.

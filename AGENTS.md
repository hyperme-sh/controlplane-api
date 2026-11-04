# API package development

Read README.md. Shared implementations live under src/controlplane_api.
Preserve HTTP routes, payloads, settings binding and process-local registry state.
Import no legacy api or product implementation. Operator plugin registration is
for trusted local code. Consumer alias compatibility requires separate tests.

Run bash scripts/check-package.sh with read access to the pinned identity and
events repositories. Keep full dependency SHAs in standard package metadata and
uv.lock. Validate source, fresh-wheel and rebuilt-sdist contexts. Keep Actions
disabled until scoped dependency access and shared-runner qualification are configured.

## Package publication permission boundary

Source/package validation keeps its existing runner policy and read-only contents.
The separate `.github/workflows/release.yml` publication job is the narrow exception:
it may use `contents: write` and `actions: read` on disposable `ubuntu-24.04` workers
solely through the exact-pinned shared package publisher. It must not check out or
execute this repository's code, install its packages, or receive private dependency
or deployment credentials. This hosted publication exception does not authorize
moving secret-bearing validation to another runner group. Stable publication must
retain any configured release-admission prerequisite for the exact tag/commit.

# API package development

Read README.md. Shared implementations live under src/controlplane_api.
Preserve HTTP routes, payloads, settings binding and process-local registry state.
Import no legacy api or product implementation. Operator plugin registration is
for trusted local code. Consumer alias compatibility requires separate tests.

Run bash scripts/check-package.sh with read access to the pinned identity and
events repositories. Keep full dependency SHAs in standard package metadata and
uv.lock. Validate source, fresh-wheel and rebuilt-sdist contexts. Keep Actions
disabled until scoped dependency access and hosted-worker policy are configured.

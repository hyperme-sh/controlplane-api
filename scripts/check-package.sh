#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
unset PYTHONPATH UV_NO_SYNC
python3 scripts/check_open_boundary.py src pyproject.toml
sync_options=()
run_options=()
export_options=()
fixture_wheels=()
case "${1:-}" in
  '') uv lock --check ;;
  --fixtures)
    fixture_paths=$(python3 scripts/verify_dependency_fixtures.py "$PWD")
    mapfile -t fixture_wheels <<< "$fixture_paths"
    run_options=(--no-sync)
    sync_options+=(--no-install-package controlplane-identity)
    export_options+=(--no-emit-package controlplane-identity)
    sync_options+=(--no-install-package controlplane-events)
    export_options+=(--no-emit-package controlplane-events)
    ;;
  *) echo 'Usage: bash scripts/check-package.sh [--fixtures]' >&2; exit 2 ;;
esac
if (( $# > 1 )); then echo 'Unexpected arguments' >&2; exit 2; fi
sync_environment() {
  uv sync --frozen --python 3.13 "${sync_options[@]}"
  if (( ${#fixture_wheels[@]} )); then
    uv pip install --python .venv/bin/python --no-deps --reinstall "${fixture_wheels[@]}"
  fi
}
scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT
if [[ -n "${RELEASE_CANDIDATE_DIR:-}" ]]; then
  # This is a disposable copy of the immutable Actions artifact, never an upload source.
  mkdir -p "$scratch/dist"
  cp "$RELEASE_CANDIDATE_DIR"/*.whl "$RELEASE_CANDIDATE_DIR"/*.tar.gz "$scratch/dist/"
else
  sync_environment
  uv build --out-dir "$scratch/dist"
fi
# Validate the fresh candidate before running any source tests or installing code.
distribution_hashes=$(cd "$scratch/dist" && sha256sum -- *.whl *.tar.gz)
python3 scripts/verify_wheel.py "$scratch/dist"
sync_environment
uv run --frozen "${run_options[@]}" pytest --junitxml="$scratch/source.xml"
uv run --frozen "${run_options[@]}" pytest -q tests_tools
uv run --frozen "${run_options[@]}" python scripts/export_release_contract.py "$scratch"/dist/*.whl --output "$scratch/contract"
# Keep historical contracts intact. Only the exact reviewed, artifact-derived
# compatibility transition may produce a fresh development qualification.
uv run --frozen "${run_options[@]}" python scripts/qualify_health_metadata.py "$scratch"/dist/*.whl --output "$scratch/qualification"
uv run --frozen "${run_options[@]}" python scripts/verify_release_candidate.py "$scratch/qualification/release.json" "$scratch/contract/contract.json" "$scratch/contract/evidence.json" controlplane-api
uv export --frozen "${export_options[@]}" --no-emit-project --format requirements-txt --output-file "$scratch/requirements.txt" >/dev/null
uv venv --python 3.13 "$scratch/venv"
uv pip sync --python "$scratch/venv/bin/python" "$scratch/requirements.txt"
if (( ${#fixture_wheels[@]} )); then
  uv pip install --python "$scratch/venv/bin/python" --no-deps "${fixture_wheels[@]}" "$scratch"/dist/*.whl
else
  uv pip uninstall --python "$scratch/venv/bin/python" controlplane-identity controlplane-events
  uv pip install --python "$scratch/venv/bin/python" --constraint "$scratch/requirements.txt" "$scratch"/dist/*.whl
fi
cp -R tests "$scratch/"
(cd "$scratch" && "$scratch/venv/bin/python" -I -m pytest -c /dev/null tests --junitxml="$scratch/wheel.xml")
# Rebuild from the sdist; a checkout must not supply omitted package files.
uv run --frozen "${run_options[@]}" python - "$scratch" <<'PY'
import pathlib, sys, tarfile
root = pathlib.Path(sys.argv[1])
with tarfile.open(next((root / 'dist').glob('*.tar.gz'))) as archive:
    archive.extractall(root / 'sdist', filter='data')
PY
uv build --wheel "$scratch"/sdist/* --out-dir "$scratch/rebuilt"
uv run --frozen "${run_options[@]}" python scripts/verify_wheel.py "$scratch/rebuilt"
uv run --frozen "${run_options[@]}" python scripts/export_release_contract.py "$scratch"/rebuilt/*.whl --output "$scratch/rebuilt-contract"
cmp "$scratch/contract/contract.json" "$scratch/rebuilt-contract/contract.json"
if (( ${#fixture_wheels[@]} )); then
  uv pip install --python "$scratch/venv/bin/python" --no-deps --reinstall "$scratch"/rebuilt/*.whl
else
  uv pip install --python "$scratch/venv/bin/python" --constraint "$scratch/requirements.txt" --reinstall "$scratch"/rebuilt/*.whl
  uv pip check --python "$scratch/venv/bin/python"
fi
(cd "$scratch" && "$scratch/venv/bin/python" -I -m pytest -c /dev/null tests --junitxml="$scratch/sdist.xml")

# Installed tests may inspect these files, but must not replace validated bytes.
(cd "$scratch/dist" && sha256sum --check <<< "$distribution_hashes")

python3 scripts/verify-test-results.py "$scratch/source.xml" "$scratch/wheel.xml" "$scratch/sdist.xml"
if [[ -n "${TEST_EVIDENCE_DIR:-}" ]]; then
  mkdir -p "$TEST_EVIDENCE_DIR"
  cp "$scratch"/*.xml "$TEST_EVIDENCE_DIR/"
  cp "$scratch/qualification/compatibility.json" "$TEST_EVIDENCE_DIR/"
fi

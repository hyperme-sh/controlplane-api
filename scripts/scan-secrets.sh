#!/usr/bin/env bash
set -euo pipefail
scratch=$(mktemp -d "${RUNNER_TEMP:-/tmp}/cli-scanner.XXXXXX")
trap 'rm -rf -- "$scratch"' EXIT
archive=gitleaks_8.30.1_linux_x64.tar.gz
curl --fail --silent --show-error --location "https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/$archive" -o "$scratch/$archive"
printf '%s  %s\n' 551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb "$scratch/$archive" | sha256sum --check
tar -xzf "$scratch/$archive" -C "$scratch" gitleaks
"$scratch/gitleaks" dir "$1" --redact --no-banner --ignore-gitleaks-allow --max-archive-depth 3

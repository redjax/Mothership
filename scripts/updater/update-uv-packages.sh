#!/usr/bin/env bash
set -euo pipefail

if ! command -v uv >&/dev/null; then
  echo "[ERROR] uv is not installed" >&2
  exit 1
fi

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CWD="$(pwd)"

function cleanup() {
  cd "${CWD}"
}
trap cleanup EXIT

echo "Updating uv packages"
echo ""

cd "${THIS_DIR}"

uv lock --upgrade

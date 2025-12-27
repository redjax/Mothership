#!/usr/bin/env bash
set -uo pipefail

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT=$(realpath -m "$THIS_DIR/../..")
SUBMODULES_DIR="${REPO_ROOT}/modules"

GIT_DIR_REPO="${SUBMODULES_DIR}/git_dir"

DEST_DIR="${HOME}/git"

function usage() {
    echo ""
    echo "Usage: ${0} [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help         Print this help menu"
    echo "  -t, --target-path  Path where the git_dir submodule should be linked."
    echo "  --dry-run          Describe actions that would be taken instead of actually taking them."
    echo ""
}

TARGET_PATH=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case $1 in
    -t|--target)
      if [[ -z "${2:-}" ]]; then
        echo "[ERROR] --target-path provided, but no target directory path given."
        usage
        exit 1
      fi

      TARGET_PATH="${2}"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    -h|--help)
      usage

      exit 0
      ;;
    *)
      echo "[ERROR] Invalid arg: $1"
      usage

      exit 1
      ;;
  esac
done

if [[ -n "${TARGET_PATH:-}" ]]; then
  DEST_DIR="$(realpath -m "${TARGET_PATH}")"
fi

## Ensure the git_dir submodule actually exists
if [[ ! -d "${GIT_DIR_REPO}" ]]; then
  echo "[ERROR] Submodule path does not exist: ${GIT_DIR_REPO}"
  exit 1
fi

## If destination exists, exit with error
if [[ -e "${DEST_DIR}" ]]; then
  echo "[ERROR] Destination already exists: ${DEST_DIR}"
  exit 1
fi

## Ensure we have an absolute path for the link target
LINK_TARGET="$(realpath -m "${GIT_DIR_REPO}")"

## Create parent directory if needed (in case DEST_DIR's parent doesn't exist)
DEST_PARENT="$(dirname "${DEST_DIR}")"
if [[ ! -d "${DEST_PARENT}" ]]; then
  if [[ "$DRY_RUN" == true ]]; then
    echo "[DRY RUN] Would create directory: ${DEST_PARENT}"
  else
    mkdir -p "${DEST_PARENT}"
  fi
fi

## Create the symlink using an absolute path
if [[ "$DRY_RUN" == true ]]; then
  echo "[DRY RUN] Would create symlink:"
  echo "          Source: ${LINK_TARGET}"
  echo "          Target: ${DEST_DIR}"
  echo ""
else
  ln -s "${LINK_TARGET}" "${DEST_DIR}"
  echo "Linked ${DEST_DIR} -> ${LINK_TARGET}"
fi

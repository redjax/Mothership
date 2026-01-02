#!/usr/bin/env bash
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DEPLOY_PY=$(realpath -m "${SCRIPT_DIR}/../deploy/do_deployment.py")
BINARY_NAME="deploy"
OUTPUT_DIR=$(realpath -m "${SCRIPT_DIR}/../../bin")

## Platform detection
if [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="linux"
else
    echo "[ERROR] Unsupported platform: $OSTYPE (only macOS/Linux supported)"
    exit 1
fi

echo "[INFO] Building for platform: $PLATFORM"

## Ensure Python script exists
if [[ ! -f "$DEPLOY_PY" ]]; then
    echo "[ERROR] Python script not found: $DEPLOY_PY"
    exit 1
fi

## Ensure output directory
mkdir -p "$OUTPUT_DIR"

## Check if pyinstaller already available (highest priority)
if command -v pyinstaller >/dev/null 2>&1; then
    echo "[INFO] PyInstaller already available"
    BUILD_TOOL="pyinstaller"
elif command -v mise >/dev/null 2>&1; then
    echo "[INFO] Using mise to install pyinstaller"

    eval "$(mise activate bash)"
    if [[ -f .mise.toml ]]; then
        mise trust
        eval "$(mise activate bash)"
    fi

    pipx install pyinstaller
    BUILD_TOOL="pyinstaller"

elif command -v pipx >/dev/null 2>&1; then
    echo "[INFO] Using pipx to install pyinstaller"

    pipx install pyinstaller
    BUILD_TOOL="pyinstaller"
else
    echo "[ERROR] No supported build tool found:"
    echo "  - pyinstaller (not in PATH)"
    echo "  - mise (not installed)"
    echo "  - pipx (not installed)"
    echo ""
    echo "Install one of:"
    echo "  curl https://mise.run | sh  # mise (recommended)"
    echo "  pip install --user pipx   # pipx"
    echo ""
    exit 1
fi

## Build binary
echo "[INFO] Building ${BINARY_NAME} with ${BUILD_TOOL}..."
cd "$SCRIPT_DIR/../.."

if [[ "$BUILD_TOOL" == "pyinstaller" ]]; then
    pyinstaller \
        --onefile \
        --name "$BINARY_NAME" \
        --distpath "$OUTPUT_DIR" \
        --workpath "/tmp/pyinstaller-work" \
        --specpath "/tmp/pyinstaller-spec" \
        "$DEPLOY_PY"
    
    ## Make executable
    chmod +x "$OUTPUT_DIR/$BINARY_NAME"
    
    echo ""
    echo "[SUCCESS] Binary created: $OUTPUT_DIR/$BINARY_NAME"
    echo "[INFO] Size: $(du -h "$OUTPUT_DIR/$BINARY_NAME" | cut -f1)"
    echo "[INFO] Platform: $PLATFORM"
    echo ""
    echo "Usage:"
    echo "  $OUTPUT_DIR/$BINARY_NAME -m ~/Mothership"
    echo "  $OUTPUT_DIR/$BINARY_NAME -c my-deploy.json"
else
    echo "[ERROR] Unsupported build tool: $BUILD_TOOL"
    exit 1
fi

echo "[SUCCESS] Packaging complete!"

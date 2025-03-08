#!/bin/bash
# Script to generate requirements.txt for the base Docker image

set -e

REPO_ROOT=$(pwd)
OUTPUT_DIR="$REPO_ROOT/dockerfiles/base/python"
OUTPUT_FILE="$OUTPUT_DIR/requirements.txt"

# Default subfolders to scan
SUBFOLDERS=("agent_c_core" "agent_c_api_ui" "agent_c_tools")
if [ $# -gt 0 ]; then
    SUBFOLDERS=("$@")
fi

# Run the dependency scanner with the specified subfolders
python3 "$REPO_ROOT/ci/dependency_scanner.py" "$REPO_ROOT" "$OUTPUT_FILE" "${SUBFOLDERS[@]}"

echo "Base dependencies have been written to $OUTPUT_FILE"
echo "You can now use this in your Dockerfile:"
echo "COPY requirements.txt /tmp/"
echo "RUN pip install --no-cache-dir -r /tmp/requirements.txt"
#!/usr/bin/env bash
set -euo pipefail
exec docker run --rm \
  --network host \
  --user "$(id -u):$(id -g)" \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  -e SECRET_KEY \
  -e SCANCODEIO_DB_NAME \
  -e SCANCODEIO_DB_USER \
  -e SCANCODEIO_DB_PASSWORD \
  -e SCANCODEIO_DB_HOST=localhost \
  -e SCANCODEIO_WORKSPACE_LOCATION \
  -v "$GITHUB_WORKSPACE:/workspace" \
  "$SCANCODEIO_IMAGE" \
  scanpipe "$@"

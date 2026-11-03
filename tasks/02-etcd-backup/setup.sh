#!/usr/bin/env bash
set -euo pipefail
# Ensure docker CLI can reach the control-plane; nothing else to pre-seed.
CP="${CLUSTER_NAME}-control-plane"
docker exec "$CP" mkdir -p /opt/cka
# Remove any previous snapshot so candidates must create it
docker exec "$CP" rm -f /opt/cka/etcd-snapshot.db || true

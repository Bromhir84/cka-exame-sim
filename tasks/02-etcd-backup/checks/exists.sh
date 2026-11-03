#!/usr/bin/env bash
set -euo pipefail

CP="${CLUSTER_NAME}-control-plane"
SIZE=$(docker exec "$CP" sh -c 'if [ -f /opt/cka/etcd-snapshot.db ]; then wc -c < /opt/cka/etcd-snapshot.db; else echo 0; fi' | tr -d ' ')
[ "${SIZE:-0}" -ge 1000 ]

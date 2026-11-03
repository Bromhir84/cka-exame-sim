#!/usr/bin/env bash
set -euo pipefail

CP="${CLUSTER_NAME}-control-plane"

# Snapshot file must exist and be non-empty
SIZE=$(docker exec "$CP" sh -c 'if [ -f /opt/cka/etcd-snapshot.db ]; then wc -c < /opt/cka/etcd-snapshot.db; else echo 0; fi' | tr -d ' ')
if [ "${SIZE:-0}" -lt 1000 ]; then
  echo "snapshot missing or too small: $SIZE bytes"
  exit 1
fi

# Validate snapshot status via etcdctl inside the node if available, else accept size check
docker exec "$CP" sh -c '
  if command -v etcdctl >/dev/null 2>&1; then
    ETCDCTL_API=3 etcdctl --write-out=table snapshot status /opt/cka/etcd-snapshot.db >/dev/null
  fi
'

exit 0

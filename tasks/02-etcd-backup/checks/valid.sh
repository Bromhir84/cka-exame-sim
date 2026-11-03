#!/usr/bin/env bash
set -euo pipefail

CP="${CLUSTER_NAME}-control-plane"
docker exec "$CP" sh -c '
  if command -v etcdctl >/dev/null 2>&1; then
    ETCDCTL_API=3 etcdctl --write-out=table snapshot status /opt/cka/etcd-snapshot.db >/dev/null
  elif [ -f /opt/cka/etcd-snapshot.db ]; then
    test $(wc -c < /opt/cka/etcd-snapshot.db) -ge 1000
  else
    exit 1
  fi
'

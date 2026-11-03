## Goal
Take a consistent etcd snapshot on the kind control-plane and save it to `/opt/cka/etcd-snapshot.db` **inside that node**.

## Steps
```bash
CP="${CLUSTER_NAME}-control-plane"

docker exec "$CP" mkdir -p /opt/cka

docker exec "$CP" sh -c 'ETCDCTL_API=3 etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  snapshot save /opt/cka/etcd-snapshot.db'
```

## Verify
```bash
docker exec "$CP" ls -lh /opt/cka/etcd-snapshot.db
docker exec "$CP" sh -c 'ETCDCTL_API=3 etcdctl --write-out=table snapshot status /opt/cka/etcd-snapshot.db'
```

## Notes
- Cert paths are under `/etc/kubernetes/pki/etcd/` on kubeadm/kind nodes.
- The file must exist on the **control-plane container**, not on your laptop.

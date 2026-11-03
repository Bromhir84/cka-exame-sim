# Task 2 — etcd Backup (15%)

Take a consistent etcd snapshot of the cluster control plane and save it to:

`/opt/cka/etcd-snapshot.db`

on the **control-plane node** of this kind cluster.

Hints:

- Cluster name is available as `$CLUSTER_NAME` in your shell.
- Control-plane container is typically `$(echo $CLUSTER_NAME)-control-plane`.
- You can `docker exec` into the control-plane and use `ETCDCTL_API=3 etcdctl` with the certificates under `/etc/kubernetes/pki/etcd/`.
- Ensure the directory `/opt/cka` exists inside the control-plane container before saving.

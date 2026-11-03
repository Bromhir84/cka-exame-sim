## Goal
Custom StorageClass + PVC referencing it.

## Steps
```bash
kubectl apply -f - <<'EOF'
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-local
provisioner: rancher.io/local-path
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
EOF
kubectl -n stor-sc-custom apply -f - <<'EOF'
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: fast-pvc
  namespace: stor-sc-custom
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: fast-local
  resources:
    requests: {storage: 1Gi}
EOF
```

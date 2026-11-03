## Goal
ROX PVC Bound.

## Steps
```bash
kubectl apply -f - <<'EOF'
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-ro99
spec:
  capacity: {storage: 1Gi}
  accessModes: [ReadOnlyMany]
  storageClassName: manual-99
  hostPath: {path: /mnt/ro99}
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ro-claim
  namespace: stor-ro99
spec:
  accessModes: [ReadOnlyMany]
  storageClassName: manual-99
  resources:
    requests: {storage: 1Gi}
EOF
```

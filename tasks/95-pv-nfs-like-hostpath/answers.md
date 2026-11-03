## Goal
Static hostPath PV.

## Steps
```bash
kubectl apply -f - <<'EOF'
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-host-95
spec:
  capacity:
    storage: 5Gi
  accessModes: [ReadWriteOnce]
  storageClassName: manual-95
  persistentVolumeReclaimPolicy: Retain
  hostPath:
    path: /mnt/data-95
EOF
```

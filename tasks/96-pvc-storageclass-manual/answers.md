## Goal
Static provision bind.

## Steps
```bash
kubectl apply -f - <<'EOF'
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: manual-96
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: Immediate
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-96
spec:
  capacity: {storage: 1Gi}
  accessModes: [ReadWriteOnce]
  storageClassName: manual-96
  hostPath: {path: /mnt/data-96}
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: claim-96
  namespace: stor-96
spec:
  accessModes: [ReadWriteOnce]
  storageClassName: manual-96
  resources:
    requests:
      storage: 1Gi
EOF
kubectl -n stor-96 wait --for=jsonpath='{.status.phase}'=Bound pvc/claim-96 --timeout=60s
```

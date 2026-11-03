## Goal
PVC `busy-pvc` (500Mi) + Pod mounting at `/mnt/data`.

## Steps
```bash
NS=stor-busy
kubectl -n "$NS" apply -f - <<'EOF'
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: busy-pvc
  namespace: stor-busy
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: standard
  resources:
    requests:
      storage: 500Mi
---
apiVersion: v1
kind: Pod
metadata:
  name: busy-pod
  namespace: stor-busy
spec:
  containers:
    - name: busybox
      image: busybox:1.36
      command: ["sleep", "3600"]
      volumeMounts:
        - name: data
          mountPath: /mnt/data
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: busy-pvc
EOF
kubectl -n "$NS" wait --for=condition=Ready pod/busy-pod --timeout=120s
```

## Verify
```bash
kubectl -n "$NS" get pvc busy-pvc pod busy-pod
```

## Goal
PVC `data-pvc` (1Gi, RWO, `standard`) + Pod `data-pod` mounting it at `/data`.

## Steps
```bash
NS=storage-lab

kubectl -n "$NS" apply -f - <<'EOF'
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data-pvc
  namespace: storage-lab
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: standard
  resources:
    requests:
      storage: 1Gi
---
apiVersion: v1
kind: Pod
metadata:
  name: data-pod
  namespace: storage-lab
spec:
  containers:
    - name: busybox
      image: busybox:1.36
      command: ["sleep", "3600"]
      volumeMounts:
        - name: data
          mountPath: /data
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: data-pvc
EOF

kubectl -n "$NS" wait --for=condition=Ready pod/data-pod --timeout=120s
```

## Verify
```bash
kubectl -n "$NS" get pvc data-pvc
kubectl -n "$NS" get pod data-pod
```

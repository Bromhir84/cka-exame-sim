## Goal
Mount PVC with **subPath: cache** at `/work`.

## Steps
```bash
NS=stor-sub
kubectl -n "$NS" apply -f - <<'EOF'
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: sub-pvc
  namespace: stor-sub
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
  name: sub-pod
  namespace: stor-sub
spec:
  containers:
    - name: busybox
      image: busybox:1.36
      command: ["sleep", "3600"]
      volumeMounts:
        - name: data
          mountPath: /work
          subPath: cache
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: sub-pvc
EOF
kubectl -n "$NS" wait --for=condition=Ready pod/sub-pod --timeout=120s
```

## Verify
```bash
kubectl -n "$NS" get pod sub-pod -o jsonpath='{.spec.containers[0].volumeMounts[0].subPath}{"\n"}'
```

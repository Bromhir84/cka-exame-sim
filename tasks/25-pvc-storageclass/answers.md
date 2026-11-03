## Goal
PVC `app-data` 2Gi + Pod mount at `/var/app`.

## Steps
```bash
NS=stor-sc
kubectl -n "$NS" apply -f - <<'EOF'
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: app-data
  namespace: stor-sc
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: standard
  resources:
    requests:
      storage: 2Gi
---
apiVersion: v1
kind: Pod
metadata:
  name: app-data-pod
  namespace: stor-sc
spec:
  containers:
    - name: busybox
      image: busybox:1.36
      command: ["sleep", "3600"]
      volumeMounts:
        - name: data
          mountPath: /var/app
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: app-data
EOF
kubectl -n "$NS" get pvc app-data
kubectl -n "$NS" wait --for=condition=Ready pod/app-data-pod --timeout=120s
```

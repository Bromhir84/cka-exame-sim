## Goal
5Gi PVC on `standard` + Pod mount.

## Steps
```bash
kubectl -n stor-big apply -f - <<'EOF'
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: big-data
  namespace: stor-big
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: standard
  resources:
    requests: {storage: 5Gi}
---
apiVersion: v1
kind: Pod
metadata:
  name: big-pod
  namespace: stor-big
spec:
  containers:
    - name: busybox
      image: busybox:1.36
      command: ["sleep", "3600"]
      volumeMounts:
        - {name: data, mountPath: /data}
  volumes:
    - name: data
      persistentVolumeClaim: {claimName: big-data}
EOF
```

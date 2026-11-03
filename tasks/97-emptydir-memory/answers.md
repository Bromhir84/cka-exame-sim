## Goal
tmpfs emptyDir.

## Steps
```bash
kubectl -n stor-mem97 apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: mem-pod
spec:
  containers:
  - name: c
    image: busybox:1.36
    command: ["sleep","3600"]
    volumeMounts:
    - name: cache
      mountPath: /cache
  volumes:
  - name: cache
    emptyDir:
      medium: Memory
EOF
```

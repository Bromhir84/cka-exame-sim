## Goal
Non-root UID/GID on Pod.

## Steps
```bash
kubectl -n wl-sec75 apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  securityContext:
    runAsUser: 1000
    runAsGroup: 3000
  containers:
  - name: c
    image: busybox:1.36
    command: ["sleep","3600"]
EOF
kubectl -n wl-sec75 wait --for=condition=Ready pod/secure-pod --timeout=120s
```

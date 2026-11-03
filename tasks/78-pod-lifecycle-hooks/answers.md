## Goal
postStart lifecycle hook.

## Steps
```bash
kubectl -n wl-hook78 apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: hook-pod
spec:
  containers:
  - name: c
    image: busybox:1.36
    command: ["sleep","3600"]
    lifecycle:
      postStart:
        exec:
          command: ["sh","-c","echo hooked > /tmp/hooked"]
EOF
kubectl -n wl-hook78 wait --for=condition=Ready pod/hook-pod --timeout=120s
```

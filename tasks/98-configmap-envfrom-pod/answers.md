## Goal
envFrom ConfigMap.

## Steps
```bash
kubectl -n stor-cme98 create cm cfg --from-literal=COLOR=blue
kubectl -n stor-cme98 apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: cfg-pod
spec:
  containers:
  - name: c
    image: busybox:1.36
    command: ["sleep","3600"]
    envFrom:
    - configMapRef:
        name: cfg
EOF
```

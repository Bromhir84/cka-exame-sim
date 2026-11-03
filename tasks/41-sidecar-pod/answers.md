## Goal
Multi-container Pod with `app` (nginx) and `sidecar` (busybox sleep).

## Steps
```bash
kubectl -n wl-sidecar apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: pair
  namespace: wl-sidecar
spec:
  containers:
    - name: app
      image: nginx:1.27
    - name: sidecar
      image: busybox:1.36
      command: ["sleep", "3600"]
EOF
```

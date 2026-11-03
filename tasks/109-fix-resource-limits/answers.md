## Goal
Reduce CPU request.

## Steps
```bash
kubectl -n ts-res109 delete pod heavy --force --grace-period=0
kubectl -n ts-res109 apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: heavy
spec:
  containers:
  - name: c
    image: busybox:1.36
    command: ["sleep","3600"]
    resources:
      requests: {cpu: 100m, memory: 128Mi}
      limits: {cpu: 100m, memory: 128Mi}
EOF
```

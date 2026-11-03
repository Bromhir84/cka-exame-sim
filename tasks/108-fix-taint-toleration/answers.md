## Goal
Tolerate dedicated=cka:NoSchedule.

## Steps
```bash
kubectl -n ts-taint108 delete pod critical --force --grace-period=0
kubectl -n ts-taint108 apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: critical
spec:
  tolerations:
  - key: dedicated
    operator: Equal
    value: cka
    effect: NoSchedule
  containers:
  - name: c
    image: busybox:1.36
    command: ["sleep","3600"]
EOF
kubectl -n ts-taint108 wait --for=condition=Ready pod/critical --timeout=120s
```
Cleanup note: exam end destroys the cluster.

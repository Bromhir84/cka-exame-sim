## Goal
Secret keys as env vars `DB_USER` / `DB_PASS`.

## Steps
```bash
kubectl -n stor-sec92 create secret generic db-creds \
  --from-literal=username=admin --from-literal=password=hunter2
kubectl -n stor-sec92 apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: sec-pod
spec:
  containers:
  - name: c
    image: busybox:1.36
    command: ["sleep","3600"]
    env:
    - name: DB_USER
      valueFrom:
        secretKeyRef:
          name: db-creds
          key: username
    - name: DB_PASS
      valueFrom:
        secretKeyRef:
          name: db-creds
          key: password
EOF
kubectl -n stor-sec92 wait --for=condition=Ready pod/sec-pod --timeout=120s
```

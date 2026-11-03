## Goal
SA can read pods and pod logs.

## Steps
```bash
kubectl -n arch-logs63 create sa log-reader
kubectl -n arch-logs63 apply -f - <<'EOF'
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: log-reader
  namespace: arch-logs63
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get"]
EOF
kubectl -n arch-logs63 create rolebinding log-reader-binding --role=log-reader --serviceaccount=arch-logs63:log-reader
```

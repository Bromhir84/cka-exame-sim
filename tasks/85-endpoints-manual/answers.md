## Goal
Selector-less Service + Endpoints.

## Steps
```bash
kubectl -n net-ep85 apply -f - <<'EOF'
apiVersion: v1
kind: Service
metadata:
  name: external-web
spec:
  ports:
  - port: 80
---
apiVersion: v1
kind: Endpoints
metadata:
  name: external-web
subsets:
- addresses:
  - ip: 1.2.3.4
  ports:
  - port: 80
EOF
```

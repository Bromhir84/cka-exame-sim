## Goal
Service selecting pods with **both** `tier=frontend` and `env=prod`.

## Steps
```bash
kubectl -n net-svclabel apply -f - <<'EOF'
apiVersion: v1
kind: Service
metadata:
  name: fe-svc
  namespace: net-svclabel
spec:
  selector:
    tier: frontend
    env: prod
  ports:
    - port: 80
      targetPort: 80
EOF
```

## Verify
```bash
kubectl -n net-svclabel get svc fe-svc -o yaml
kubectl -n net-svclabel get endpoints fe-svc
```

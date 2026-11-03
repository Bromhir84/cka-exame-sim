## Goal
Allow Ingress to `app=secure-db` **only** from `role=frontend` on TCP 5432.

## Steps
```bash
kubectl -n policy-lab apply -f - <<'EOF'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: db-allow-frontend
  namespace: policy-lab
spec:
  podSelector:
    matchLabels:
      app: secure-db
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              role: frontend
      ports:
        - protocol: TCP
          port: 5432
EOF
```

## Verify
```bash
kubectl -n policy-lab get networkpolicy db-allow-frontend -o yaml
```

## Notes
- Do not add an allow-all ingress rule; only the frontend source should be listed.

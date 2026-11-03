## Goal
Deny-all ingress NetworkPolicy for the whole namespace.

## Steps
```bash
kubectl -n net-deny apply -f - <<'EOF'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
  namespace: net-deny
spec:
  podSelector: {}
  policyTypes:
    - Ingress
EOF
```

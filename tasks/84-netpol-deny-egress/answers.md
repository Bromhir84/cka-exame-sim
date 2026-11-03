## Goal
Default-deny egress.

## Steps
```bash
kubectl -n net-eg84 apply -f - <<'EOF'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-egress
spec:
  podSelector: {}
  policyTypes: [Egress]
EOF
```

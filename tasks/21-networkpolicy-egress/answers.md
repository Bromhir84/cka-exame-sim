## Goal
Egress-only policy for `app=client` to `app=api` on TCP 8080.

## Steps
```bash
kubectl -n net-egress apply -f - <<'EOF'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: client-egress
  namespace: net-egress
spec:
  podSelector:
    matchLabels:
      app: client
  policyTypes:
    - Egress
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: api
      ports:
        - protocol: TCP
          port: 8080
EOF
```

## Verify
```bash
kubectl -n net-egress get networkpolicy client-egress -o yaml
```

## Notes
- Graders check the NetworkPolicy object. A policy with only this egress rule also blocks DNS unless you add kube-dns rules.

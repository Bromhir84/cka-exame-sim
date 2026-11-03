## Goal
LimitRange with default memory request 64Mi and limit 256Mi.

## Steps
```bash
kubectl -n arch-limits apply -f - <<'EOF'
apiVersion: v1
kind: LimitRange
metadata:
  name: mem-limit-range
  namespace: arch-limits
spec:
  limits:
    - type: Container
      defaultRequest:
        memory: 64Mi
      default:
        memory: 256Mi
EOF
```

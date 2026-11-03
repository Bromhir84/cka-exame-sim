## Goal
Container LimitRange defaults.

## Steps
```bash
kubectl -n arch-lr62 apply -f - <<'EOF'
apiVersion: v1
kind: LimitRange
metadata:
  name: pod-limits
spec:
  limits:
  - type: Container
    defaultRequest:
      cpu: 100m
      memory: 128Mi
    default:
      cpu: 500m
      memory: 256Mi
EOF
```

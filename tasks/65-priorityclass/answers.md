## Goal
Non-default PriorityClass.

## Steps
```bash
kubectl apply -f - <<'EOF'
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: high-priority-65
value: 1000000
globalDefault: false
description: "CKA practice high priority"
EOF
```

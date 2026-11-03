## Goal
Deployment with required nodeAffinity on `kubernetes.io/os=linux`.

## Steps
```bash
kubectl -n wl-affinity apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: placed
  namespace: wl-affinity
spec:
  replicas: 1
  selector:
    matchLabels: {app: placed}
  template:
    metadata:
      labels: {app: placed}
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
              - matchExpressions:
                  - key: kubernetes.io/os
                    operator: In
                    values: ["linux"]
      containers:
        - name: web
          image: nginx:1.27
EOF
```

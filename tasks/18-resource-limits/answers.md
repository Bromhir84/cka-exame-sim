## Goal
Deployment `limited` with the specified requests and limits.

## Steps
```bash
NS=wl-limits
kubectl -n "$NS" apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: limited
  namespace: wl-limits
spec:
  replicas: 1
  selector:
    matchLabels:
      app: limited
  template:
    metadata:
      labels:
        app: limited
    spec:
      containers:
        - name: web
          image: nginx:1.27
          resources:
            requests:
              cpu: 50m
              memory: 32Mi
            limits:
              cpu: 200m
              memory: 128Mi
EOF
kubectl -n "$NS" rollout status deploy/limited
```

## Verify
```bash
kubectl -n "$NS" get deploy limited -o jsonpath='{.spec.template.spec.containers[0].resources}'
```

## Goal
StatefulSet + headless Service.

## Steps
```bash
kubectl -n wl-sts70 apply -f - <<'EOF'
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  clusterIP: None
  selector:
    app: web
  ports:
  - port: 80
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  serviceName: web
  replicas: 2
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: nginx
        image: nginx:1.27
EOF
kubectl -n wl-sts70 rollout status statefulset/web --timeout=180s
```

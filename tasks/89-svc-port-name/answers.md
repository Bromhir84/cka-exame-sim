## Goal
Named targetPort.

## Steps
```bash
kubectl -n net-name89 apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  replicas: 1
  selector:
    matchLabels: {app: api}
  template:
    metadata:
      labels: {app: api}
    spec:
      containers:
      - name: api
        image: nginx:1.27
        ports:
        - name: http
          containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: named
spec:
  selector:
    app: api
  ports:
  - name: http
    port: 80
    targetPort: http
EOF
```

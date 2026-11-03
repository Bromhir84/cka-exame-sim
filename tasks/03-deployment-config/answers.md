## Goal
In `workloads-lab`, create ConfigMap + Secret and a 3-replica nginx Deployment that consumes both, with CPU/memory requests.

## Steps
```bash
NS=workloads-lab

kubectl -n "$NS" create configmap app-config --from-literal=APP_ENV=production
kubectl -n "$NS" create secret generic app-secret --from-literal=APP_TOKEN=s3cr3t

kubectl -n "$NS" apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: workloads-lab
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: web
          image: nginx:1.27
          env:
            - name: APP_ENV
              valueFrom:
                configMapKeyRef:
                  name: app-config
                  key: APP_ENV
            - name: APP_TOKEN
              valueFrom:
                secretKeyRef:
                  name: app-secret
                  key: APP_TOKEN
          resources:
            requests:
              cpu: 100m
              memory: 64Mi
EOF

kubectl -n "$NS" rollout status deploy/web
```

## Verify
```bash
kubectl -n "$NS" get cm app-config secret app-secret
kubectl -n "$NS" get deploy web
kubectl -n "$NS" get pods -l app=web
```

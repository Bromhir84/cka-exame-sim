## Goal
Deployment `sa-demo` must run as ServiceAccount `app-sa` in `arch-sa-deploy`.

## Steps
```bash
NS=arch-sa-deploy
kubectl -n "$NS" create sa app-sa

kubectl -n "$NS" apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sa-demo
  namespace: arch-sa-deploy
spec:
  replicas: 1
  selector:
    matchLabels:
      app: sa-demo
  template:
    metadata:
      labels:
        app: sa-demo
    spec:
      serviceAccountName: app-sa
      containers:
        - name: web
          image: nginx:1.27
EOF

kubectl -n "$NS" rollout status deploy/sa-demo
```

## Verify
```bash
kubectl -n "$NS" get deploy sa-demo -o jsonpath='{.spec.template.spec.serviceAccountName}{"\n"}'
```

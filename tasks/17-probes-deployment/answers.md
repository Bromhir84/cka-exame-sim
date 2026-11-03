## Goal
Deployment `probed` with readiness + liveness HTTP probes on `/`:80.

## Steps
```bash
NS=wl-probes
kubectl -n "$NS" apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: probed
  namespace: wl-probes
spec:
  replicas: 2
  selector:
    matchLabels:
      app: probed
  template:
    metadata:
      labels:
        app: probed
    spec:
      containers:
        - name: web
          image: nginx:1.27
          ports:
            - containerPort: 80
          readinessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 5
          livenessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 10
EOF
kubectl -n "$NS" rollout status deploy/probed
```

## Verify
```bash
kubectl -n "$NS" get deploy probed -o yaml | grep -A6 -E 'readinessProbe|livenessProbe'
```

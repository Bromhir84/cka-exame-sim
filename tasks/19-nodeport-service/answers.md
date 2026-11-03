## Goal
NodePort Service `web-nodeport` with nodePort **30080**.

## Steps
```bash
NS=net-nodeport
kubectl -n "$NS" apply -f - <<'EOF'
apiVersion: v1
kind: Service
metadata:
  name: web-nodeport
  namespace: net-nodeport
spec:
  type: NodePort
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 80
      nodePort: 30080
EOF
```

## Verify
```bash
kubectl -n "$NS" get svc web-nodeport -o yaml
```

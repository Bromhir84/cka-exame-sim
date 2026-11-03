## Goal
ClusterIP Service with named ports `http` (80→80) and `metrics` (8080→8080).

## Steps
```bash
kubectl -n net-multiport apply -f - <<'EOF'
apiVersion: v1
kind: Service
metadata:
  name: dual-svc
  namespace: net-multiport
spec:
  selector:
    app: dual
  ports:
    - name: http
      port: 80
      targetPort: 80
    - name: metrics
      port: 8080
      targetPort: 8080
EOF
```

## Verify
```bash
kubectl -n net-multiport get svc dual-svc -o yaml
```

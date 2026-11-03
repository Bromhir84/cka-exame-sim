## Goal
Expose Deployment `hello` via ClusterIP Service `hello-svc` (80→8080) and Ingress `hello-ing` for host `hello.cka.local`.

## Steps
```bash
NS=net-lab

kubectl -n "$NS" expose deploy hello --name=hello-svc --port=80 --target-port=8080

kubectl -n "$NS" apply -f - <<'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: hello-ing
  namespace: net-lab
spec:
  ingressClassName: nginx
  rules:
    - host: hello.cka.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: hello-svc
                port:
                  number: 80
EOF
```

## Verify
```bash
kubectl -n "$NS" get svc hello-svc -o wide
kubectl -n "$NS" get ingress hello-ing -o yaml
```

## Notes
- `ingressClassName: nginx` matches the kind ingress-nginx install.
- External DNS for the host is not required for grading.

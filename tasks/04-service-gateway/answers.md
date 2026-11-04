## Goal
Expose Deployment `hello` with Service `hello-svc` (80→8080), Gateway `hello-gw`, and HTTPRoute `hello-route` for `hello.cka.local`.

## Steps
```bash
NS=net-lab

kubectl -n "$NS" expose deploy hello --name=hello-svc --port=80 --target-port=8080

kubectl -n "$NS" apply -f - <<'EOF'
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: hello-gw
  namespace: net-lab
spec:
  gatewayClassName: nginx
  listeners:
    - name: http
      protocol: HTTP
      port: 80
      hostname: hello.cka.local
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: hello-route
  namespace: net-lab
spec:
  parentRefs:
    - name: hello-gw
      sectionName: http
  hostnames:
    - hello.cka.local
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /
      backendRefs:
        - name: hello-svc
          port: 80
EOF
```

## Verify
```bash
kubectl -n "$NS" get svc hello-svc
kubectl -n "$NS" get gateway hello-gw -o yaml
kubectl -n "$NS" get httproute hello-route -o yaml
```

## Notes
- GatewayClass `nginx` is preinstalled. Do not create an Ingress.
- `PathPrefix` is the Gateway API path type (Ingress called this `Prefix`).

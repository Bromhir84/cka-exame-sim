## Goal
Read Ingress `echo-ing` and replace it with Gateway `echo-gw` plus HTTPRoute `echo-route`.

## Steps
```bash
# See the host, path, and backend you must copy.
kubectl -n net-ing82 get ingress echo-ing -o yaml

kubectl -n net-ing82 apply -f - <<'EOF'
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: echo-gw
  namespace: net-ing82
spec:
  gatewayClassName: nginx
  listeners:
    - name: http
      protocol: HTTP
      port: 80
      hostname: echo.cka.local
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: echo-route
  namespace: net-ing82
spec:
  parentRefs:
    - name: echo-gw
      sectionName: http
  hostnames:
    - echo.cka.local
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /
      backendRefs:
        - name: echo
          port: 80
EOF

kubectl -n net-ing82 delete ingress echo-ing
```

## Notes
- Ingress `pathType: Prefix` becomes HTTPRoute `path.type: PathPrefix`.
- `ingressClassName` becomes `gatewayClassName` on the Gateway, not a field on the HTTPRoute.

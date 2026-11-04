## Goal
Terminate TLS on Gateway `web-gw` with Secret `web-tls`, and route HTTPS hostname `tls.cka.local` to Service `web`.

## Steps
```bash
kubectl -n net-tls86 create secret tls web-tls --cert="$HOME/tls.crt" --key="$HOME/tls.key"

kubectl -n net-tls86 apply -f - <<'EOF'
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: web-gw
  namespace: net-tls86
spec:
  gatewayClassName: nginx
  listeners:
    - name: https
      protocol: HTTPS
      port: 443
      hostname: tls.cka.local
      tls:
        mode: Terminate
        certificateRefs:
          - kind: Secret
            name: web-tls
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: web-route
  namespace: net-tls86
spec:
  parentRefs:
    - name: web-gw
      sectionName: https
  hostnames:
    - tls.cka.local
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /
      backendRefs:
        - name: web
          port: 80
EOF
```

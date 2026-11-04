## Goal
One HTTPRoute with two path rules on Gateway `split-gw`.

## Steps
```bash
kubectl -n net-mp90 apply -f - <<'EOF'
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: split
  namespace: net-mp90
spec:
  parentRefs:
    - name: split-gw
      sectionName: http
  hostnames:
    - split.cka.local
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /app
      backendRefs:
        - name: app
          port: 80
    - matches:
        - path:
            type: PathPrefix
            value: /api
      backendRefs:
        - name: api
          port: 80
EOF
```

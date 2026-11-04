## Goal
HTTPRoute `shop-route` for `/shop` on the existing Gateway `shop-gw`.

## Steps
```bash
kubectl -n net-ingpath apply -f - <<'EOF'
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: shop-route
  namespace: net-ingpath
spec:
  parentRefs:
    - name: shop-gw
      sectionName: http
  hostnames:
    - shop.cka.local
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /shop
      backendRefs:
        - name: shop
          port: 80
EOF
```

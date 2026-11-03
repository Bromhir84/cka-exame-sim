## Goal
Ingress `shop-ing` host `shop.cka.local`, path `/shop` → Service `shop:80`.

## Steps
```bash
kubectl -n net-ingpath apply -f - <<'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: shop-ing
  namespace: net-ingpath
spec:
  ingressClassName: nginx
  rules:
    - host: shop.cka.local
      http:
        paths:
          - path: /shop
            pathType: Prefix
            backend:
              service:
                name: shop
                port:
                  number: 80
EOF
```

## Verify
```bash
kubectl -n net-ingpath get ingress shop-ing -o yaml
```

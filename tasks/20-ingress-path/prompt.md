# Ingress Path

Namespace `net-ingpath` has Deployment/Service `shop` exposing port 80.

Create Ingress `shop-ing` with:

- ingressClassName: `nginx`
- host: `shop.cka.local`
- path: `/shop` (Prefix) → Service `shop` port 80

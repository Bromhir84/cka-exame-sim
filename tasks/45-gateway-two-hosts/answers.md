## Goal
One HTTPRoute per hostname, both parented to Gateway `web-gw`.

## Steps
```bash
kubectl -n net-twohost apply -f - <<'EOF'
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: alpha
  namespace: net-twohost
spec:
  parentRefs:
    - name: web-gw
  hostnames:
    - alpha.cka.local
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /
      backendRefs:
        - name: alpha-svc
          port: 80
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: beta
  namespace: net-twohost
spec:
  parentRefs:
    - name: web-gw
  hostnames:
    - beta.cka.local
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /
      backendRefs:
        - name: beta-svc
          port: 80
EOF
```

## Notes
An HTTPRoute's hostnames apply to every rule, so two backends need two HTTPRoutes.

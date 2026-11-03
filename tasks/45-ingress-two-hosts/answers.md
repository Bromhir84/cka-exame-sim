## Goal
One Ingress object with two host rules.

## Steps
```bash
kubectl -n net-twohost apply -f - <<'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: multi-ing
  namespace: net-twohost
spec:
  ingressClassName: nginx
  rules:
    - host: alpha.cka.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service: {name: alpha-svc, port: {number: 80}}
    - host: beta.cka.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service: {name: beta-svc, port: {number: 80}}
EOF
```

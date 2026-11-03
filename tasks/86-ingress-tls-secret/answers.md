## Goal
Ingress with TLS section.

## Steps
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /tmp/tls.key -out /tmp/tls.crt -subj "/CN=tls.cka.local"
kubectl -n net-tls86 create secret tls web-tls --cert=/tmp/tls.crt --key=/tmp/tls.key
kubectl -n net-tls86 apply -f - <<'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-tls-ing
spec:
  ingressClassName: nginx
  tls:
  - hosts: [tls.cka.local]
    secretName: web-tls
  rules:
  - host: tls.cka.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web
            port:
              number: 80
EOF
```

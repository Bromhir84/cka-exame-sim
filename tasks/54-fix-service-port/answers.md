## Goal
Patch Service targetPort to 8080.

## Steps
```bash
kubectl -n ts-port patch svc api-svc -p '{"spec":{"ports":[{"port":80,"targetPort":8080}]}}'
```

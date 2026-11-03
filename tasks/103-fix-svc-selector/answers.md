## Goal
Align Service selector with pods.

## Steps
```bash
kubectl -n ts-svc103 patch svc web -p '{"spec":{"selector":{"app":"web"}}}'
kubectl -n ts-svc103 get endpoints web
```

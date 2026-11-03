## Goal
Fix Service selector to match Deployment pods (`app=web`).

## Steps
```bash
kubectl -n ts-lab111 patch svc web -p '{"spec":{"selector":{"app":"web"}}}'
kubectl -n ts-lab111 get endpoints web
```

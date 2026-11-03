## Goal
ClientIP session affinity.

## Steps
```bash
kubectl -n net-aff83 expose deploy web --name=sticky --port=80
kubectl -n net-aff83 patch svc sticky -p '{"spec":{"sessionAffinity":"ClientIP"}}'
```

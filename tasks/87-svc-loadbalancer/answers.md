## Goal
Service type LoadBalancer.

## Steps
```bash
kubectl -n net-lb87 expose deploy web --name=web-lb --port=80 --type=LoadBalancer
```

## Goal
Scale to 2.

## Steps
```bash
kubectl -n ts-rep107 scale deploy/web --replicas=2
kubectl -n ts-rep107 rollout status deploy/web
```

## Goal
Scale Deployment back to 3 replicas.

## Steps
```bash
kubectl -n ts-replicas scale deploy/frontend --replicas=3
kubectl -n ts-replicas rollout status deploy/frontend
```

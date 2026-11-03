## Goal
Fix image tag.

## Steps
```bash
kubectl -n ts-img102 set image deploy/site site=nginx:1.27
kubectl -n ts-img102 rollout status deploy/site
```

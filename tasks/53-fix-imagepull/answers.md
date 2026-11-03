## Goal
Replace the invalid image with `nginx:1.27`.

## Steps
```bash
kubectl -n ts-pull set image deploy/web web=nginx:1.27
kubectl -n ts-pull rollout status deploy/web
```

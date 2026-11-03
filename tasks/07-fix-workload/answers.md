## Goal
Deployment `frontend` in `broken-app` must run image `nginx:1.27` with 2 Ready replicas. Fix in place (do not delete the Deployment).

## Investigate
```bash
kubectl -n broken-app get deploy frontend -o wide
kubectl -n broken-app describe deploy frontend
kubectl -n broken-app get pods
```

## Fix
```bash
kubectl -n broken-app set image deploy/frontend frontend=nginx:1.27
kubectl -n broken-app scale deploy/frontend --replicas=2
kubectl -n broken-app rollout status deploy/frontend
```

## Verify
```bash
kubectl -n broken-app get deploy frontend
kubectl -n broken-app get pods -o jsonpath='{range .items[*]}{.metadata.name}{" "}{.spec.containers[0].image}{"\n"}{end}'
```

## Goal
Scale Deployment `api` in `wl-scale` to 4 Ready replicas.

## Steps
```bash
kubectl -n wl-scale scale deploy/api --replicas=4
kubectl -n wl-scale rollout status deploy/api
```

## Verify
```bash
kubectl -n wl-scale get deploy api
```

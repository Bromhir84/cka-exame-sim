## Goal
Wire Secret key into Deployment env.

## Steps
```bash
kubectl -n wl-env69 create secret generic app-secret --from-literal=PASSWORD=s3cret
kubectl -n wl-env69 create deploy web --image=nginx:1.27
kubectl -n wl-env69 set env deploy/web --from=secret/app-secret
kubectl -n wl-env69 rollout status deploy/web
```

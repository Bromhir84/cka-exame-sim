## Goal
envFrom ConfigMap on Deployment.

## Steps
```bash
kubectl -n wl-envfrom76 create cm app-config --from-literal=APP_MODE=prod --from-literal=LOG_LEVEL=info
kubectl -n wl-envfrom76 create deploy api --image=nginx:1.27
kubectl -n wl-envfrom76 set env deploy/api --from=configmap/app-config
kubectl -n wl-envfrom76 rollout status deploy/api
```

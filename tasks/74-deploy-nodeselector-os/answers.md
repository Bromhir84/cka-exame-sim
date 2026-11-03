## Goal
Schedule only on linux nodes.

## Steps
```bash
kubectl -n wl-os74 create deploy linux-web --image=nginx:1.27
kubectl -n wl-os74 patch deploy linux-web -p '{"spec":{"template":{"spec":{"nodeSelector":{"kubernetes.io/os":"linux"}}}}}'
kubectl -n wl-os74 rollout status deploy/linux-web
```

## Goal
RollingUpdate with maxUnavailable 0.

## Steps
```bash
kubectl -n wl-roll72 create deploy api --image=nginx:1.27 --replicas=3
kubectl -n wl-roll72 patch deploy api -p '{"spec":{"strategy":{"type":"RollingUpdate","rollingUpdate":{"maxUnavailable":0,"maxSurge":1}}}}'
kubectl -n wl-roll72 rollout status deploy/api
```

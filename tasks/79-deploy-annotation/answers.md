## Goal
Pod template annotation.

## Steps
```bash
kubectl -n wl-ann79 create deploy annotated --image=nginx:1.27
kubectl -n wl-ann79 patch deploy annotated --type=merge -p '{"spec":{"template":{"metadata":{"annotations":{"cka.exam/owner":"team-a"}}}}}'
kubectl -n wl-ann79 rollout status deploy/annotated
```

## Goal
Replace failing command with sleep.

## Steps
```bash
kubectl -n ts-crash101 patch deploy worker -p '{"spec":{"template":{"spec":{"containers":[{"name":"worker","image":"busybox:1.36","command":["sleep","3600"]}]}}}}'
kubectl -n ts-crash101 rollout status deploy/worker
```

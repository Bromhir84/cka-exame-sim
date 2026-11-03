## Goal
Create missing ConfigMap `app-settings` with `mode=online` so Deployment `cfg-app` becomes Ready.

## Investigate
```bash
kubectl -n ts-cm describe deploy cfg-app
kubectl -n ts-cm get events --sort-by=.lastTimestamp | tail
```

## Fix
```bash
kubectl -n ts-cm create configmap app-settings --from-literal=mode=online
kubectl -n ts-cm rollout restart deploy/cfg-app
kubectl -n ts-cm rollout status deploy/cfg-app
```

## Verify
```bash
kubectl -n ts-cm get cm app-settings
kubectl -n ts-cm get deploy cfg-app
```

## Goal
liveness path /.

## Steps
```bash
kubectl -n ts-live112 patch deploy api --type=json -p='[{"op":"replace","path":"/spec/template/spec/containers/0/livenessProbe/httpGet/path","value":"/"}]'
kubectl -n ts-live112 rollout status deploy/api
```

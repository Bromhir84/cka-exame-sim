## Goal
Point readiness at /.

## Steps
```bash
kubectl -n ts-ready104 patch deploy api --type=json -p='[{"op":"replace","path":"/spec/template/spec/containers/0/readinessProbe/httpGet/path","value":"/"}]'
kubectl -n ts-ready104 rollout status deploy/api
```

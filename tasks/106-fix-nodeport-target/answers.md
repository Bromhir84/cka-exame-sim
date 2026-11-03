## Goal
targetPort 80.

## Steps
```bash
kubectl -n ts-port106 patch svc web --type=json -p='[{"op":"replace","path":"/spec/ports/0/targetPort","value":80}]'
```

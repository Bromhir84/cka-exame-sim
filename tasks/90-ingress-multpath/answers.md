## Goal
Two paths on one host.

## Steps
```bash
kubectl -n net-mp90 create ingress split --class=nginx \
  --rule='split.cka.local/app=app:80' \
  --rule='split.cka.local/api=api:80'
```

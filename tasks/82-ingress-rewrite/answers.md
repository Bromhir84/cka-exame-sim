## Goal
Host-based Ingress.

## Steps
```bash
kubectl -n net-ing82 create ingress echo-ing --class=nginx --rule='echo.cka.local/*=echo:80'
```

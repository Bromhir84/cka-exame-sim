## Goal
NodePort 30080.

## Steps
```bash
kubectl -n net-np80 create deploy web --image=nginx:1.27
kubectl -n net-np80 label deploy web app=web --overwrite
kubectl -n net-np80 expose deploy web --name=web-np --port=80 --type=NodePort
kubectl -n net-np80 patch svc web-np -p '{"spec":{"ports":[{"port":80,"targetPort":80,"nodePort":30080}]}}'
```

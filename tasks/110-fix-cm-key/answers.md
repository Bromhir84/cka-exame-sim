## Goal
Add missing ConfigMap key.

## Steps
```bash
kubectl -n ts-cm110 create cm app-cm --from-literal=config=hello --from-literal=app.conf=hello -o yaml --dry-run=client | kubectl apply -f -
kubectl -n ts-cm110 wait --for=condition=Ready pod/need-cm --timeout=120s
```

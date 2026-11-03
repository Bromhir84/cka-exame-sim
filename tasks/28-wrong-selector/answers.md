## Goal
Service `backend-svc` must select pods labeled `app=backend` and have Endpoints.

## Investigate
```bash
kubectl -n ts-selector get deploy,po,svc,ep -o wide
kubectl -n ts-selector get svc backend-svc -o yaml
kubectl -n ts-selector get pods --show-labels
```

## Fix
```bash
kubectl -n ts-selector patch svc backend-svc -p '{"spec":{"selector":{"app":"backend"}}}'
```

## Verify
```bash
kubectl -n ts-selector get endpoints backend-svc
```

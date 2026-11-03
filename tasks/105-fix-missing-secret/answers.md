## Goal
Create the referenced Secret.

## Steps
```bash
kubectl -n ts-sec105 create secret generic app-secret --from-literal=config=ok
kubectl -n ts-sec105 wait --for=condition=Ready pod/need-secret --timeout=120s
```

## Goal
Namespaced read-only access to Secrets for SA `secret-reader` in `arch-secrets`.

## Steps
```bash
NS=arch-secrets
kubectl -n "$NS" create sa secret-reader
kubectl -n "$NS" create role secret-reader-role \
  --verb=get,list,watch --resource=secrets
kubectl -n "$NS" create rolebinding secret-reader-binding \
  --role=secret-reader-role \
  --serviceaccount=arch-secrets:secret-reader
```

## Verify
```bash
kubectl -n "$NS" auth can-i get secrets --as=system:serviceaccount:arch-secrets:secret-reader
kubectl -n "$NS" auth can-i delete secrets --as=system:serviceaccount:arch-secrets:secret-reader
# expect "no" for delete
```

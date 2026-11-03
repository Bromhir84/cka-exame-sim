## Goal
Allow SA `svc-manager` to get/list/create/delete Services in `arch-svc-rbac`.

## Steps
```bash
NS=arch-svc-rbac
kubectl -n "$NS" create sa svc-manager
kubectl -n "$NS" create role svc-manager-role \
  --verb=get,list,create,delete --resource=services
kubectl -n "$NS" create rolebinding svc-manager-binding \
  --role=svc-manager-role \
  --serviceaccount=arch-svc-rbac:svc-manager
```

## Verify
```bash
kubectl -n "$NS" auth can-i create services --as=system:serviceaccount:arch-svc-rbac:svc-manager
```

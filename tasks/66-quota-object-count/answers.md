## Goal
Object-count ResourceQuota.

## Steps
```bash
kubectl -n arch-count66 create quota object-counts --hard=pods=10,services=5,secrets=10,configmaps=10
```

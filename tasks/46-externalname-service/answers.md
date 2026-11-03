## Goal
ExternalName Service to `www.example.com`.

## Steps
```bash
kubectl -n net-ext create service externalname search-ext --external-name=www.example.com
```

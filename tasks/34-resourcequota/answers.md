## Goal
Create ResourceQuota `team-quota` with the specified hard limits.

## Steps
```bash
kubectl -n arch-quota create quota team-quota \
  --hard=requests.cpu=2,requests.memory=2Gi,pods=10
```

## Verify
```bash
kubectl -n arch-quota describe quota team-quota
```

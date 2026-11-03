## Goal
Namespace compute ResourceQuota.

## Steps
```bash
kubectl -n arch-quota61 create quota compute-quota --hard=requests.cpu=1,requests.memory=1Gi,limits.cpu=2,limits.memory=2Gi
```

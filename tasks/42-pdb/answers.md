## Goal
PDB with minAvailable 1 for `app=api`.

## Steps
```bash
kubectl -n wl-pdb create poddisruptionbudget api-pdb --selector=app=api --min-available=1
```

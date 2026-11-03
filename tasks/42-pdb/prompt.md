# PodDisruptionBudget

Namespace `wl-pdb` has Deployment `api` with label `app=api`.

Create PodDisruptionBudget `api-pdb` that:

- selects `app=api`
- `minAvailable: 1`

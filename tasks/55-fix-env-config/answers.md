## Goal
Provide ConfigMap `worker-config` with MODE=batch.

## Steps
```bash
kubectl -n ts-env create configmap worker-config --from-literal=MODE=batch
kubectl -n ts-env rollout restart deploy/worker
kubectl -n ts-env rollout status deploy/worker
```

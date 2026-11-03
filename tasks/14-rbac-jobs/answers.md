## Goal
SA `job-runner` can manage batch Jobs in `arch-jobs`.

## Steps
```bash
NS=arch-jobs
kubectl -n "$NS" create sa job-runner
kubectl -n "$NS" create role job-runner-role \
  --verb=get,list,create,delete \
  --resource=jobs.batch
kubectl -n "$NS" create rolebinding job-runner-binding \
  --role=job-runner-role \
  --serviceaccount=arch-jobs:job-runner
```

## Verify
```bash
kubectl -n "$NS" auth can-i create jobs.batch --as=system:serviceaccount:arch-jobs:job-runner
```

## Notes
- Resource must be `jobs` in API group `batch` (`jobs.batch` with `create role`).

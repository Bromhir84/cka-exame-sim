## Goal
Pod `stuck` is Pending due to an impossible nodeSelector—remove/fix it; keep image `nginx:1.27`.

## Investigate
```bash
kubectl -n ts-pending get pod stuck -o wide
kubectl -n ts-pending describe pod stuck
```

## Fix
```bash
kubectl -n ts-pending patch pod stuck --type=json \
  -p='[{"op":"remove","path":"/spec/nodeSelector"}]'

# If immutable fields block the patch, delete and recreate without nodeSelector
# (same name, image nginx:1.27).
```

## Verify
```bash
kubectl -n ts-pending get pod stuck
```

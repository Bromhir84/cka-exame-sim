## Goal
Stop CrashLoopBackOff on `looper` by using command `sleep 3600` and image `busybox:1.36`. Do not delete the Deployment.

## Investigate
```bash
kubectl -n ts-crash get pods
kubectl -n ts-crash logs deploy/looper
kubectl -n ts-crash describe deploy looper | tail -40
```

## Fix
```bash
kubectl -n ts-crash set image deploy/looper='*=busybox:1.36'
kubectl -n ts-crash edit deploy looper
# Set containers[0].command to ["sleep","3600"] and image busybox:1.36

# Or patch (adjust container name if needed):
kubectl -n ts-crash get deploy looper -o jsonpath='{.spec.template.spec.containers[0].name}{"\n"}'
kubectl -n ts-crash patch deploy looper --type=strategic -p '{
  "spec":{"template":{"spec":{"containers":[{"name":"CONTAINER","image":"busybox:1.36","command":["sleep","3600"]}]}}}
}'
kubectl -n ts-crash rollout status deploy/looper
```

## Verify
```bash
kubectl -n ts-crash get deploy looper
```

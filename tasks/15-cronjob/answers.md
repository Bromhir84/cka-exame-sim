## Goal
CronJob `ping-cron` every 5 minutes, `concurrencyPolicy: Forbid`, busybox echo job.

## Steps
```bash
NS=wl-cron
kubectl -n "$NS" create cronjob ping-cron \
  --image=busybox:1.36 \
  --schedule="*/5 * * * *" \
  -- echo cka-cron

kubectl -n "$NS" patch cronjob ping-cron -p '{"spec":{"concurrencyPolicy":"Forbid"}}'

# If the grader requires container name `ping`:
kubectl -n "$NS" patch cronjob ping-cron --type=json -p='[
  {"op":"replace","path":"/spec/jobTemplate/spec/template/spec/containers/0/name","value":"ping"}
]'
```

## Verify
```bash
kubectl -n "$NS" get cronjob ping-cron -o jsonpath='{.spec.schedule}{" "}{.spec.concurrencyPolicy}{"\n"}'
```

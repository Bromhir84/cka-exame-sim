## Goal
CronJob with Forbid concurrency.

## Steps
```bash
kubectl -n wl-cron71 create cronjob tick --image=busybox:1.36 --schedule='*/5 * * * *' -- sh -c 'date; echo tick'
kubectl -n wl-cron71 patch cronjob tick -p '{"spec":{"concurrencyPolicy":"Forbid","successfulJobsHistoryLimit":1,"failedJobsHistoryLimit":1}}'
```

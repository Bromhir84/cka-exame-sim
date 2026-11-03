# CronJob

In namespace `wl-cron71` create CronJob `tick` that:

- schedule: `*/5 * * * *`
- image `busybox:1.36`
- command `["sh","-c","date; echo tick"]`
- `concurrencyPolicy: Forbid`
- successfulJobsHistoryLimit 1, failedJobsHistoryLimit 1

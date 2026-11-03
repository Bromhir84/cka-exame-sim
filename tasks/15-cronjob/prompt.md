# CronJob

In namespace `wl-cron`, create CronJob `ping-cron` that:

- schedule: `*/5 * * * *`
- concurrencyPolicy: `Forbid`
- job template runs a container named `ping` with image `busybox:1.36` and command `["echo","cka-cron"]`

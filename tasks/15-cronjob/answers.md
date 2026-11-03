## Solution
`kubectl -n wl-cron create cronjob ping-cron --image=busybox:1.36 --schedule='*/5 * * * *' -- echo cka-cron` then set concurrencyPolicy=Forbid.

# Job

In namespace `wl-job` create Job `pi-job` that:

- uses image `busybox:1.36`
- container name `worker`
- command: `["sh","-c","echo 3.14 && exit 0"]`
- `restartPolicy: Never`
- `backoffLimit: 2`

The Job should succeed (Complete).

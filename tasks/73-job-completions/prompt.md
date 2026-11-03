# Job completions

In namespace `wl-comp73` create Job `batch` with:

- `completions: 3`
- `parallelism: 1`
- image `busybox:1.36`
- command `["sh","-c","echo done"]`
- restartPolicy Never

Wait until the Job is Complete.

## Goal
Create a completing Job with Never restart and backoffLimit 2.

## Steps
```bash
kubectl -n wl-job create job pi-job --image=busybox:1.36 -- sh -c 'echo 3.14 && exit 0'
kubectl -n wl-job patch job pi-job -p '{"spec":{"backoffLimit":2}}'
# ensure restartPolicy Never (default for jobs)
kubectl -n wl-job wait --for=condition=Complete job/pi-job --timeout=120s
```

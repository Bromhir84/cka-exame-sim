## Goal
Scale ReplicaSet to 4.

## Steps
```bash
kubectl -n wl-rs77 scale rs/web --replicas=4
kubectl -n wl-rs77 wait --for=jsonpath='{.status.readyReplicas}'=4 rs/web --timeout=120s
```

## Goal
Allow an SA to read Events.

## Steps
```bash
kubectl -n arch-events60 create sa event-watcher
kubectl -n arch-events60 create role event-watcher-role --verb=get,list,watch --resource=events
kubectl -n arch-events60 create rolebinding event-watcher-binding --role=event-watcher-role --serviceaccount=arch-events60:event-watcher
```

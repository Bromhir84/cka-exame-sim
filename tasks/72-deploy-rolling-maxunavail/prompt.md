# Deployment strategy

In namespace `wl-roll72` create Deployment `api` (3 replicas, `nginx:1.27`) with RollingUpdate strategy:

- `maxUnavailable: 0`
- `maxSurge: 1`

Deployment must become Ready.

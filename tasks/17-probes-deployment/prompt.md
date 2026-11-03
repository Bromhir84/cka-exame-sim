# Probes

In namespace `wl-probes`, create Deployment `probed` with:

- 2 replicas, image `nginx:1.27`, container name `web`
- readinessProbe: HTTP GET path `/` port `80`, initialDelaySeconds `5`
- livenessProbe: HTTP GET path `/` port `80`, initialDelaySeconds `10`

Ensure Ready.

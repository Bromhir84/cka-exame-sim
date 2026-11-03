# Resource Limits

In namespace `wl-limits`, create Deployment `limited` with 1 replica, image `nginx:1.27`, container `web`, and:

- requests: cpu `50m`, memory `32Mi`
- limits: cpu `200m`, memory `128Mi`

Ensure Ready.

# Deployment + Secret env

In namespace `wl-env69`:

1. Secret `app-secret` with key `PASSWORD` = `s3cret`
2. Deployment `web` (1 replica, `nginx:1.27`, container `web`) with env var `PASSWORD` from that Secret key
3. Deployment must be Ready

# envFrom ConfigMap

In namespace `wl-envfrom76`:

1. ConfigMap `app-config` with `APP_MODE=prod` and `LOG_LEVEL=info`
2. Deployment `api` (`nginx:1.27`) using `envFrom` → that ConfigMap
3. Ready

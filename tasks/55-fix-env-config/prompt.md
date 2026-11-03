# Broken env

Namespace `ts-env` has Deployment `worker` expecting env `MODE` from ConfigMap `worker-config` key `MODE`.

The ConfigMap is missing or wrong. Create/fix ConfigMap `worker-config` with `MODE=batch` so the Deployment becomes Ready (1 replica). Prefer fixing the ConfigMap.

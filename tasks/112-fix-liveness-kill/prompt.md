# Crash from liveness

Namespace `ts-live112` Deployment `api` restarts forever: livenessProbe httpGet path `/healthz` (404). Change path to `/` (keep the probe). Ready.

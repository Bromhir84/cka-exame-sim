# Task 3 — Workloads & Scheduling (15%)

In namespace `workloads-lab`, create:

1. ConfigMap `app-config` with key `APP_ENV=production`
2. Secret `app-secret` of type Opaque with key `APP_TOKEN` value `s3cr3t` (plain string; kubectl will encode)
3. Deployment `web` with:
   - **3** replicas
   - image `nginx:1.27`
   - container name `web`
   - env var `APP_ENV` from ConfigMap `app-config` key `APP_ENV`
   - env var `APP_TOKEN` from Secret `app-secret` key `APP_TOKEN`
   - CPU request `100m` and memory request `64Mi`

Ensure all pods become Ready.

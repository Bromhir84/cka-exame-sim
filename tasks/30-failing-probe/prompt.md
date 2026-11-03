# Bad Readiness Probe

Namespace `ts-probe` has Deployment `web` that never becomes Ready because the readinessProbe path is wrong.

Fix the probe so it checks HTTP `/` on port 80 (nginx). Keep 2 replicas and image `nginx:1.27`.

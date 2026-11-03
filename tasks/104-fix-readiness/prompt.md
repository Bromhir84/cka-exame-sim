# Ready replicas 0

Namespace `ts-ready104` Deployment `api` never becomes Ready due to a readinessProbe hitting the wrong path. Fix the probe to use path `/` on port 80 (httpGet). Do not remove the probe.

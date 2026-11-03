# Labeled Service

Namespace `net-svclabel` has Pods labeled `tier=frontend` and `env=prod` (Deployment `fe`).

Create ClusterIP Service `fe-svc` that:

- selects pods with **both** `tier=frontend` and `env=prod`
- exposes port **80** → targetPort **80**

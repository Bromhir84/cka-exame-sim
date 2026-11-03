# Multi-host Ingress

Namespace `net-twohost` has Services `alpha-svc` and `beta-svc` (port 80).

Create Ingress `multi-ing` with `ingressClassName: nginx` and rules:

1. host `alpha.cka.local` path `/` (Prefix) → `alpha-svc:80`
2. host `beta.cka.local` path `/` (Prefix) → `beta-svc:80`

# Ingress multi-path

Namespace `net-mp90` has Services `app` and `api` on port 80. Create Ingress `split` (class nginx), host `split.cka.local`:

- path `/app` Prefix → service `app:80`
- path `/api` Prefix → service `api:80`

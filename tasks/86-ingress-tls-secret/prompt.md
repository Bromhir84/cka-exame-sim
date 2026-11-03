# Ingress TLS

Namespace `net-tls86` has Service `web` on port 80. Create TLS Secret `web-tls` (type kubernetes.io/tls) with dummy cert/key, and Ingress `web-tls-ing` (class nginx) for host `tls.cka.local` path `/` → `web:80` referencing that TLS secret.

# Secret volume

In namespace `stor-secvol`:

1. Create Secret `app-tls` (Opaque) with key `token` value `sekrit`
2. Create Pod `sec-pod` (busybox:1.36, `sleep 3600`) mounting the Secret at `/var/run/secrets/app`

Pod must be Ready.

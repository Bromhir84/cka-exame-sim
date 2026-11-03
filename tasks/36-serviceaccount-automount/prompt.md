# ServiceAccount automount

In namespace `arch-automount`:

1. Create ServiceAccount `no-token-sa` with `automountServiceAccountToken: false`
2. Create Pod `quiet` using image `busybox:1.36`, command `sleep 3600`, `serviceAccountName: no-token-sa`
3. Ensure the Pod also has `automountServiceAccountToken: false` (pod spec)

Pod must become Ready.

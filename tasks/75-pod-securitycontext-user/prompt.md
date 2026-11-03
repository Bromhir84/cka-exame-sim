# Pod securityContext

In namespace `wl-sec75` create Pod `secure-pod` using `busybox:1.36` with command `sleep 3600` and pod-level securityContext:

- `runAsUser: 1000`
- `runAsGroup: 3000`

Pod must be Ready.

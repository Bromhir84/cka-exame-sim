# Sidecar Pod

In namespace `wl-sidecar` create Pod `pair` with two containers:

1. `app` — image `nginx:1.27`
2. `sidecar` — image `busybox:1.36`, command `["sleep","3600"]`

Both must be Running / Pod Ready.

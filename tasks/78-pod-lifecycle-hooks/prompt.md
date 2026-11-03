# Lifecycle hook

In namespace `wl-hook78` create Pod `hook-pod` (`busybox:1.36`, `sleep 3600`) with a `postStart` exec hook that runs `["sh","-c","echo hooked > /tmp/hooked"]`.

Pod Ready.

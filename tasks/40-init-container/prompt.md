# Init container

In namespace `wl-init` create Pod `bootstrap` that:

1. Has initContainer `setup` using `busybox:1.36` running `["sh","-c","echo ready > /work/ok"]` mounting emptyDir `shared` at `/work`
2. Has container `app` using `busybox:1.36` running `["sh","-c","sleep 3600"]` mounting the same volume at `/data`

Pod must become Ready.

# PVC subPath

In namespace `stor-sub`:

1. PVC `sub-pvc`: 1Gi, ReadWriteOnce, StorageClass `standard`
2. Pod `sub-pod` using `busybox:1.36` / `sleep 3600`
3. Mount `sub-pvc` at `/work` using **subPath** `cache`

Ensure Ready and Bound.

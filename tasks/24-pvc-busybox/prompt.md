# PVC + busybox

In namespace `stor-busy`:

1. PVC `busy-pvc`: 500Mi, ReadWriteOnce, StorageClass `standard`
2. Pod `busy-pod`: image `busybox:1.36`, command `sleep 3600`, mount PVC at `/mnt/data`

Ensure Bound + Ready.

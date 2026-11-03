# Task 6 — Storage (10%)

In namespace `storage-lab`:

1. Create a PersistentVolumeClaim named `data-pvc` requesting **1Gi** storage, access mode **ReadWriteOnce**, using StorageClass `standard`.
2. Create a Pod named `data-pod` that:
   - uses image `busybox:1.36`
   - runs `sleep 3600`
   - mounts the PVC at `/data`

Ensure the PVC is Bound and the Pod is Ready.

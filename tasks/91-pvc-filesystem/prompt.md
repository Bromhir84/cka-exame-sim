# PVC

A 2Gi hostPath PersistentVolume with empty `storageClassName` is already available.

In namespace `stor-pvc91`:

1. Create PVC `data-pvc` requesting **2Gi**, accessMode **ReadWriteOnce**, `storageClassName: ""`
2. Create Pod `data-pod` (`busybox:1.36`, `sleep 3600`) mounting that PVC at `/data`

PVC must become Bound and the Pod Ready.

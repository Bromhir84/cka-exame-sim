# StorageClass PVC

In namespace `stor-sc`, create PVC `app-data` requesting **2Gi**, accessModes **ReadWriteOnce**, storageClassName **standard**.

Also create Pod `app-data-pod` (busybox:1.36, sleep 3600) mounting it at `/var/app`.

PVC must become Bound.

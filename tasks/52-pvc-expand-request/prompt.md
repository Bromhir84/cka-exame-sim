# PVC size

In namespace `stor-big` create PVC `big-data` requesting **5Gi**, accessModes **ReadWriteOnce**, storageClassName **standard**.

Create Pod `big-pod` (busybox:1.36, sleep 3600) mounting it at `/data`. Ensure Bound + Ready.

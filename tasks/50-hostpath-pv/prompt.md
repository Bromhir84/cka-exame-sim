# Static provisioning

In namespace `stor-hostpath`:

1. Create PersistentVolume `hp-pv` with capacity **1Gi**, accessMode **ReadWriteOnce**, hostPath `/tmp/cka-hp-pv`, storageClassName `manual`
2. Create PVC `hp-pvc` requesting **1Gi**, RWO, storageClassName `manual`
3. Create Pod `hp-pod` (busybox:1.36, sleep 3600) mounting `hp-pvc` at `/data`

PVC must Bind; Pod must be Ready.

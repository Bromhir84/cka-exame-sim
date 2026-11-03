# PVC access mode

In namespace `stor-ro99` create PVC `ro-claim` requesting 1Gi with accessModes **ReadOnlyMany** and storageClassName `manual-99`.

Also create PV `pv-ro99` (1Gi, ReadOnlyMany, storageClassName `manual-99`, hostPath `/mnt/ro99`) so the claim can Bind.

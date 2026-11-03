# PVC + PV pair

Create StorageClass `manual-96` (no-provisioner). Create PV `pv-96` (1Gi, RWO, storageClassName `manual-96`, hostPath `/mnt/data-96`). In namespace `stor-96` create PVC `claim-96` (1Gi, RWO, storageClassName `manual-96`) and ensure it becomes Bound.

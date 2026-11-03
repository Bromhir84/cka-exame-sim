# StorageClass

Create StorageClass `fast-local` with:

- provisioner: `rancher.io/local-path` (same as kind's standard class family; use this exact provisioner string)
- `reclaimPolicy: Delete`
- `volumeBindingMode: WaitForFirstConsumer`

Then in namespace `stor-sc-custom` create PVC `fast-pvc` using that StorageClass, **1Gi**, RWO (does not need to Bind yet).

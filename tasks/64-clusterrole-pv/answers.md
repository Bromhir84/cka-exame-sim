## Goal
Cluster-wide PV read access.

## Steps
```bash
kubectl -n arch-pv64 create sa pv-viewer
kubectl create clusterrole pv-viewer --verb=get,list,watch --resource=persistentvolumes
kubectl create clusterrolebinding pv-viewer-binding --clusterrole=pv-viewer --serviceaccount=arch-pv64:pv-viewer
```

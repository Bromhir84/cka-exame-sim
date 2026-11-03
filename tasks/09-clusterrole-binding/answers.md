## Goal
Cluster-scoped node read access for SA `node-inspector` in `arch-crb`.

## Steps
```bash
kubectl create clusterrole node-viewer --verb=get,list,watch --resource=nodes
kubectl -n arch-crb create sa node-inspector
kubectl create clusterrolebinding node-viewer-binding \
  --clusterrole=node-viewer \
  --serviceaccount=arch-crb:node-inspector
```

## Verify
```bash
kubectl auth can-i list nodes --as=system:serviceaccount:arch-crb:node-inspector
kubectl get clusterrole node-viewer
kubectl get clusterrolebinding node-viewer-binding
```

## Goal
Cluster-scoped node read access for an SA.

## Steps
```bash
kubectl -n arch-nodes58 create sa node-inspector
kubectl create clusterrole node-inspector --verb=get,list --resource=nodes
kubectl create clusterrolebinding node-inspector-binding --clusterrole=node-inspector --serviceaccount=arch-nodes58:node-inspector
```

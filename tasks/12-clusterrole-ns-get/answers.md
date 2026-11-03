## Goal
ClusterRole to get/list Namespaces, bound to SA `ns-auditor` in `arch-ns`.

## Steps
```bash
kubectl create clusterrole ns-lister --verb=get,list --resource=namespaces
kubectl -n arch-ns create sa ns-auditor
kubectl create clusterrolebinding ns-lister-binding \
  --clusterrole=ns-lister \
  --serviceaccount=arch-ns:ns-auditor
```

## Verify
```bash
kubectl auth can-i list namespaces --as=system:serviceaccount:arch-ns:ns-auditor
```

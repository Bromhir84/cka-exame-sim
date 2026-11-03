## Goal
ClusterRole for pod reads, bound **only** in `arch-pods` via RoleBinding.

## Steps
```bash
kubectl create clusterrole pods-reader --verb=get,list,watch --resource=pods
kubectl -n arch-pods create sa pod-auditor
kubectl -n arch-pods create rolebinding pods-reader-binding \
  --clusterrole=pods-reader \
  --serviceaccount=arch-pods:pod-auditor
```

## Verify
```bash
kubectl -n arch-pods auth can-i list pods --as=system:serviceaccount:arch-pods:pod-auditor
kubectl get clusterrolebinding pods-reader-binding 2>/dev/null || echo "no CRB (good)"
```

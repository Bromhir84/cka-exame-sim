## Goal
Namespaced Role for ConfigMap reads bound to an SA.

## Steps
```bash
kubectl -n arch-cm57 create sa cm-reader
kubectl -n arch-cm57 create role cm-reader-role --verb=get,list,watch --resource=configmaps
kubectl -n arch-cm57 create rolebinding cm-reader-binding --role=cm-reader-role --serviceaccount=arch-cm57:cm-reader
```

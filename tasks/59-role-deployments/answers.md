## Goal
Full Deployment management Role bound to SA.

## Steps
```bash
kubectl -n arch-deploy59 create sa deployer
kubectl -n arch-deploy59 create role deploy-manager --verb=create,get,list,update,patch,delete --resource=deployments.apps
kubectl -n arch-deploy59 create rolebinding deploy-manager-binding --role=deploy-manager --serviceaccount=arch-deploy59:deployer
```

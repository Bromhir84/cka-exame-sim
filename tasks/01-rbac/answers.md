## Solution
```bash
kubectl -n rbac-lab create sa deployer
kubectl -n rbac-lab create role deployer-role --verb=get,list,watch,create,update,delete --resource=pods,deployments.apps
kubectl -n rbac-lab create rolebinding deployer-binding --role=deployer-role --serviceaccount=rbac-lab:deployer
```

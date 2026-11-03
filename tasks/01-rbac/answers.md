## Goal
Create namespaced RBAC so ServiceAccount `deployer` can manage pods and deployments in `rbac-lab` only (no ClusterRole).

## Steps
```bash
kubectl -n rbac-lab create sa deployer

kubectl -n rbac-lab create role deployer-role \
  --verb=get,list,watch,create,update,delete \
  --resource=pods,deployments.apps

kubectl -n rbac-lab create rolebinding deployer-binding \
  --role=deployer-role \
  --serviceaccount=rbac-lab:deployer
```

## Verify
```bash
kubectl -n rbac-lab get sa deployer
kubectl -n rbac-lab get role deployer-role -o yaml
kubectl -n rbac-lab auth can-i create pods --as=system:serviceaccount:rbac-lab:deployer
kubectl -n rbac-lab auth can-i create deployments.apps --as=system:serviceaccount:rbac-lab:deployer
```

## Notes
- Use `deployments.apps` (or YAML with `apiGroups: ["apps"]`) so deployments are in the apps group.
- Do **not** create a ClusterRoleBinding for this task.

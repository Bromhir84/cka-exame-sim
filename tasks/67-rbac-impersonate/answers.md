## Goal
Impersonation ClusterRole for admins practice.

## Steps
```bash
kubectl -n arch-imp67 create sa impersonator
kubectl apply -f - <<'EOF'
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: user-impersonator
rules:
- apiGroups: [""]
  resources: ["users"]
  verbs: ["impersonate"]
EOF
kubectl create clusterrolebinding user-impersonator-binding --clusterrole=user-impersonator --serviceaccount=arch-imp67:impersonator
```

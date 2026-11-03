# ClusterRole + RoleBinding

Create:

1. ClusterRole `pods-reader` allowing `get`, `list`, and `watch` on `pods`
2. ServiceAccount `pod-auditor` in namespace `arch-pods`
3. **RoleBinding** (namespaced) `pods-reader-binding` in `arch-pods` that binds ClusterRole `pods-reader` to that ServiceAccount

Namespace `arch-pods` already exists. Use a RoleBinding referencing the ClusterRole (not a ClusterRoleBinding).

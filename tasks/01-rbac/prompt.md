# Task 1 — RBAC (10%)

In namespace `rbac-lab`, create:

1. A ServiceAccount named `deployer`
2. A Role named `deployer-role` that allows `get`, `list`, `watch`, `create`, `update`, and `delete` on `pods` and `deployments` (apps API group for deployments)
3. A RoleBinding named `deployer-binding` that binds `deployer-role` to ServiceAccount `deployer` in `rbac-lab`

Do not grant cluster-wide permissions.

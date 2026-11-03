# Role — Deployments

In namespace `arch-deploy59` create Role `deploy-manager` that allows `create`, `get`, `list`, `update`, `patch`, and `delete` on `deployments` in API group `apps`.

Also create ServiceAccount `deployer` and RoleBinding `deploy-manager-binding` linking them.

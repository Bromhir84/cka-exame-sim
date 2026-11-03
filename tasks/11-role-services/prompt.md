# Services Role

In namespace `arch-svc-rbac`, create:

1. ServiceAccount `svc-manager`
2. Role `svc-manager-role` with verbs `get`, `list`, `create`, `delete` on resource `services`
3. RoleBinding `svc-manager-binding` linking them

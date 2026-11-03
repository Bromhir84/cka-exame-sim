# Secrets Reader RBAC

In namespace `arch-secrets`:

1. Create ServiceAccount `secret-reader`
2. Create Role `secret-reader-role` allowing `get`, `list`, and `watch` on `secrets`
3. Create RoleBinding `secret-reader-binding` binding that Role to the ServiceAccount

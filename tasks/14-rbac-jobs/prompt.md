# Jobs RBAC

In namespace `arch-jobs`:

1. ServiceAccount `job-runner`
2. Role `job-runner-role` allowing `get`, `list`, `create`, `delete` on `jobs` in API group `batch`
3. RoleBinding `job-runner-binding` binding the Role to the ServiceAccount

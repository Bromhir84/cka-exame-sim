# Role — ConfigMaps

In namespace `arch-cm57` create:

1. ServiceAccount `cm-reader`
2. Role `cm-reader-role` allowing `get`, `list`, `watch` on `configmaps`
3. RoleBinding `cm-reader-binding` binding that Role to the ServiceAccount

Namespace exists.

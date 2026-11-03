# ClusterRole Binding

Create:

1. ClusterRole `node-viewer` that allows `get`, `list`, and `watch` on `nodes`
2. ServiceAccount `node-inspector` in namespace `arch-crb`
3. ClusterRoleBinding `node-viewer-binding` that binds ClusterRole `node-viewer` to that ServiceAccount

Namespace `arch-crb` already exists.

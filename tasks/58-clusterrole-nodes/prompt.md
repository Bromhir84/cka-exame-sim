# ClusterRole — nodes

Create:

1. ServiceAccount `node-inspector` in namespace `arch-nodes58`
2. ClusterRole `node-inspector` allowing `get` and `list` on `nodes`
3. ClusterRoleBinding `node-inspector-binding` binding that ClusterRole to the ServiceAccount

Namespace exists.

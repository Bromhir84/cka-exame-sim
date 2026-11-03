# Namespace Lister

Create ClusterRole `ns-lister` allowing `get` and `list` on `namespaces`.

Create ServiceAccount `ns-auditor` in namespace `arch-ns`.

Create ClusterRoleBinding `ns-lister-binding` binding `ns-lister` to that ServiceAccount.

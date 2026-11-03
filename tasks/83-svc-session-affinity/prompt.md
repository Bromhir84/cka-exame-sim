# Session affinity

In namespace `net-aff83` create Service `sticky` (ClusterIP) selecting `app=web`, port 80, with `sessionAffinity: ClientIP`.

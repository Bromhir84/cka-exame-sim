# Egress deny

In namespace `net-eg84` create NetworkPolicy `deny-egress` selecting all pods (`podSelector: {}`) with policyTypes `Egress` and **no egress rules** (deny all egress).

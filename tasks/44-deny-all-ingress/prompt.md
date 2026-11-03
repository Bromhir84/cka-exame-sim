# Default deny

Namespace `net-deny` has Pod `web` (label `app=web`).

Create NetworkPolicy `deny-all-ingress` that:

- selects **all pods** in the namespace (empty podSelector)
- policyTypes: **Ingress**
- has **no** ingress rules (deny all ingress)

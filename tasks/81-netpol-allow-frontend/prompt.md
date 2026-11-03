# NetworkPolicy ingress

In namespace `net-np81` create NetworkPolicy `allow-frontend` that:

- selects pods with `app=backend`
- policyTypes Ingress
- allows Ingress from pods with `app=frontend` on TCP port 80

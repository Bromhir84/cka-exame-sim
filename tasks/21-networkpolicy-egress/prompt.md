# Egress NetworkPolicy

Namespace `net-egress` has Pod `client` with label `app=client`.

Create NetworkPolicy `client-egress` that:

- selects `app=client`
- policyTypes: **Egress**
- allows egress only to pods with label `app=api` in the same namespace on TCP port **8080**

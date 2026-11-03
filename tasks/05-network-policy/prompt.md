# Task 5 — NetworkPolicy (10%)

Namespace `policy-lab` has:

- Pod `secure-db` with label `app=secure-db` (listening on TCP 5432)
- Pod `frontend` with label `role=frontend`

Create a NetworkPolicy named `db-allow-frontend` in `policy-lab` that:

1. Selects pods with `app=secure-db`
2. Uses policy type **Ingress**
3. Allows ingress **only** from pods with label `role=frontend` in the same namespace on TCP port **5432**

Do not allow all traffic.

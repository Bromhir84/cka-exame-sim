## Solution
Create NetworkPolicy `db-allow-frontend` selecting `app=secure-db`, policyTypes Ingress, from `role=frontend`, port 5432/TCP.

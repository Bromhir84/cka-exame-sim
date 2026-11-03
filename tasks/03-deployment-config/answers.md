## Solution
Create ConfigMap `app-config`, Secret `app-secret`, then Deployment `web` with 3 replicas of `nginx:1.27`, envFrom cm/secret keyRefs, and cpu/memory requests.

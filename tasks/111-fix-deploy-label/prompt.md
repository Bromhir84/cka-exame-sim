# Broken Service selector

Namespace `ts-lab111` has Deployment `web` (pods labeled `app=web`) and Service `web` selecting `app=www` (wrong). Fix the Service so it selects `app=web` and has endpoints. Do not delete the Service.

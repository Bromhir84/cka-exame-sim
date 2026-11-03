# Wrong Service Selector

Namespace `ts-selector` has Deployment `backend` (pods labeled `app=backend`) and Service `backend-svc` that does not select those pods.

Fix the Service so it selects `app=backend` and has Endpoints. Port should remain 80 → 80.

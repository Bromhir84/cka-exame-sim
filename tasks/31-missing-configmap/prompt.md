# Missing ConfigMap

Namespace `ts-cm` has Deployment `cfg-app` that fails because it mounts ConfigMap `app-settings` which does not exist.

Create ConfigMap `app-settings` with key `mode=online` (or otherwise fix the Deployment) so 1 replica becomes Ready. Prefer creating the missing ConfigMap.

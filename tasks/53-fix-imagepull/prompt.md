# ImagePullBackOff

Namespace `ts-pull` has Deployment `web` stuck pulling a bad image.

Fix it so pods run `nginx:1.27` and the Deployment has 1 Ready replica. Do not delete the Deployment.

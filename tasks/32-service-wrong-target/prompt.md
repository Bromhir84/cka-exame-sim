# Wrong targetPort

Namespace `ts-target` has Deployment `echo` listening on container port **8080**, but Service `echo-svc` targets port **80**.

Fix the Service so traffic on port 80 reaches targetPort **8080**. Selector `app=echo` should remain.

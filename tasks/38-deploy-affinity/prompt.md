# nodeAffinity

In namespace `wl-affinity` create Deployment `placed` with:

- 1 replica, image `nginx:1.27`, container `web`
- requiredDuringSchedulingIgnoredDuringExecution nodeAffinity requiring label `kubernetes.io/os` In `linux`

Ensure the Deployment is Ready.

# StatefulSet

In namespace `wl-sts70` create StatefulSet `web` with:

- 2 replicas
- serviceName `web`
- container `nginx` image `nginx:1.27`
- label `app=web` on pod template and selector

Also create headless Service `web` (`clusterIP: None`) selecting `app=web`. Pods should become Ready.

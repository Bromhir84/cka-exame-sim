# NodePort

Namespace `net-nodeport` has Deployment `web` (label `app=web`) on container port 80.

Create Service `web-nodeport` of type **NodePort**, port **80**, targetPort **80**, nodePort **30080**, selector `app=web`.

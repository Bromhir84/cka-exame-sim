# Named ports

In namespace `net-name89` create Service `named` selecting `app=api`, with port name `http`, port 8080, targetPort `http` (string). Deployment `api` should expose containerPort name `http` on 8080 (`nginx:1.27` is fine if you map 8080—or use busybox nc; simplest: Deployment with containerPort name http = 80 and Service port 80 name http).

Use: containerPort **80** named `http`, Service port **80** named `http`, targetPort `http`.

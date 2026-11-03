# Task 4 — Service & Ingress (10%)

Namespace `net-lab` already has Deployment `hello` (label `app=hello`) listening on container port 8080.

1. Create a ClusterIP Service named `hello-svc` that selects `app=hello` and exposes port **80** targeting container port **8080**.
2. Create an Ingress named `hello-ing` in `net-lab` with:
   - host `hello.cka.local`
   - path `/` (Prefix)
   - backend Service `hello-svc` port 80
   - ingress class name `nginx`

You do not need to make the host resolve externally; the grader checks resource configuration.

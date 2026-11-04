# Service and Gateway

Namespace `net-lab` already has Deployment `hello` (label `app=hello`) listening on container port 8080.

GatewayClass `nginx` is already installed. Grading checks the objects you create, not live traffic.

1. Create a ClusterIP Service named `hello-svc` that selects `app=hello` and exposes port **80** targeting container port **8080**.
2. Create Gateway `hello-gw` in `net-lab`:
   - `gatewayClassName: nginx`
   - one listener named `http`, protocol `HTTP`, port **80**, hostname `hello.cka.local`
3. Create HTTPRoute `hello-route` in `net-lab` that:
   - attaches to Gateway `hello-gw`
   - hostname `hello.cka.local`
   - matches path `/` with type `PathPrefix`
   - sends traffic to Service `hello-svc` port **80**

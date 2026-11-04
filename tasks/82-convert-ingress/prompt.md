# Convert an Ingress to Gateway API

Namespace `net-ing82` has Service `echo` and Ingress `echo-ing`. Read that Ingress and replace it with Gateway API. Do not change the Service.

GatewayClass `nginx` is already installed. Grading checks object configuration, not live traffic.

1. Create Gateway `echo-gw`:
   - `gatewayClassName: nginx`
   - one listener named `http`, protocol `HTTP`, port **80**
   - listener hostname equal to the Ingress host
2. Create HTTPRoute `echo-route` attached to Gateway `echo-gw`:
   - the same hostname
   - the same path, as type `PathPrefix`
   - the same Service name and port
3. Delete Ingress `echo-ing`.

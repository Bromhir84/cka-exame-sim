# Gateway TLS

Namespace `net-tls86` has Service `web` on port 80.

GatewayClass `nginx` is already installed.

1. Create TLS Secret `web-tls` (type `kubernetes.io/tls`) with a certificate and key for `tls.cka.local`. A self-signed certificate is enough.
2. Create Gateway `web-gw`:
   - `gatewayClassName: nginx`
   - one listener named `https`, protocol `HTTPS`, port **443**, hostname `tls.cka.local`
   - TLS mode `Terminate`, certificate reference Secret `web-tls`
3. Create HTTPRoute `web-route` attached to listener `https` on Gateway `web-gw`, hostname `tls.cka.local`, path `/` (`PathPrefix`) → Service `web` port 80.

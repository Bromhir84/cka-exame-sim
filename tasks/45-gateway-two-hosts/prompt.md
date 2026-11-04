# Two hostnames

Namespace `net-twohost` has Services `alpha-svc` and `beta-svc` (port 80) and Gateway `web-gw` (class `nginx`) listening on HTTP port 80.

Create two HTTPRoutes, both attached to `web-gw`:

1. HTTPRoute `alpha`: hostname `alpha.cka.local`, path `/` (`PathPrefix`) → `alpha-svc` port 80
2. HTTPRoute `beta`: hostname `beta.cka.local`, path `/` (`PathPrefix`) → `beta-svc` port 80

# HTTPRoute path

Namespace `net-ingpath` has Deployment/Service `shop` on port 80, and Gateway `shop-gw` (class `nginx`) with listener `http` on port 80 for hostname `shop.cka.local`.

Create HTTPRoute `shop-route` that attaches to Gateway `shop-gw` and sends hostname `shop.cka.local`, path `/shop` (`PathPrefix`), to Service `shop` port 80.

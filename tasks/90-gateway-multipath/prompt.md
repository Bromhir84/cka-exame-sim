# HTTPRoute with two paths

Namespace `net-mp90` has Services `app` and `api` on port 80, and Gateway `split-gw` (class `nginx`) with listener `http` on port 80 for hostname `split.cka.local`.

Create HTTPRoute `split` attached to `split-gw`, hostname `split.cka.local`:

- path `/app` (`PathPrefix`) → Service `app` port 80
- path `/api` (`PathPrefix`) → Service `api` port 80

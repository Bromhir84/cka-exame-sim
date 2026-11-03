## Goal
Headless Service for `app=store`.

## Steps
```bash
kubectl -n net-headless create service clusterip store-hs --clusterip=None --tcp=80:80
kubectl -n net-headless label svc store-hs unused=x --overwrite  # ensure exists
kubectl -n net-headless patch svc store-hs -p '{"spec":{"selector":{"app":"store"},"clusterIP":"None"}}'
```

Or apply YAML with `clusterIP: None` and selector `app: store`.

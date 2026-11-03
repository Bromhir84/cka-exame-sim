## Goal
Fix readinessProbe so nginx is probed at HTTP `/` on port 80. Keep 2 replicas and `nginx:1.27`.

## Investigate
```bash
kubectl -n ts-probe get deploy web -o yaml | grep -A10 readinessProbe
kubectl -n ts-probe describe pod -l app=web | grep -i ready
```

## Fix
```bash
kubectl -n ts-probe patch deploy web --type=json -p='[
  {"op":"replace","path":"/spec/template/spec/containers/0/readinessProbe/httpGet/path","value":"/"}
]'
kubectl -n ts-probe rollout status deploy/web
```

## Verify
```bash
kubectl -n ts-probe get deploy web
```

## Goal
Service `echo-svc` port 80 must target container port **8080**. Keep selector `app=echo`.

## Investigate
```bash
kubectl -n ts-target get deploy echo -o yaml | grep -A3 containerPort
kubectl -n ts-target get svc echo-svc -o yaml
kubectl -n ts-target get endpoints echo-svc
```

## Fix
```bash
kubectl -n ts-target patch svc echo-svc \
  -p '{"spec":{"ports":[{"port":80,"targetPort":8080}]}}'
```

## Verify
```bash
kubectl -n ts-target get svc echo-svc -o jsonpath='{.spec.ports[0].targetPort}{"\n"}'
kubectl -n ts-target get endpoints echo-svc
```

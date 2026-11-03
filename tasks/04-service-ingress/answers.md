## Solution
```bash
kubectl -n net-lab expose deploy hello --name=hello-svc --port=80 --target-port=8080
# create Ingress hello-ing with host hello.cka.local, class nginx, backend hello-svc:80
```

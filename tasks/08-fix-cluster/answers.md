## Goal
Restore CoreDNS so `coredns` in `kube-system` is Ready and the Corefile is valid. Backup ConfigMap `coredns-backup` is provided.

## Investigate
```bash
kubectl -n kube-system get deploy coredns
kubectl -n kube-system get cm coredns -o yaml
kubectl -n kube-system logs -l k8s-app=kube-dns --tail=50
```

## Fix
```bash
kubectl -n kube-system get cm coredns-backup -o jsonpath='{.data.Corefile}' > /tmp/Corefile
kubectl -n kube-system create configmap coredns --from-file=Corefile=/tmp/Corefile \
  -o yaml --dry-run=client | kubectl apply -f -

kubectl -n kube-system rollout restart deploy/coredns
kubectl -n kube-system rollout status deploy/coredns
```

## Verify
```bash
kubectl -n kube-system get pods -l k8s-app=kube-dns
kubectl -n kube-system get cm coredns -o jsonpath='{.data.Corefile}{"\n"}'
```

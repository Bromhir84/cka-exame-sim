## Goal
SA wired to a dockerconfig pull secret.

## Steps
```bash
kubectl -n arch-pull68 create secret docker-registry regcred \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username=dummy --docker-password=dummy --docker-email=a@b.c
kubectl -n arch-pull68 create sa puller
kubectl -n arch-pull68 patch sa puller -p '{"imagePullSecrets":[{"name":"regcred"}]}'
```

#!/usr/bin/env bash
set -euo pipefail
MP=$(kubectl -n stor-secvol get pod sec-pod -o jsonpath='{.spec.containers[0].volumeMounts[0].mountPath}')
[ "$MP" = "/var/run/secrets/app" ]
SRC=$(kubectl -n stor-secvol get pod sec-pod -o jsonpath='{.spec.volumes[0].secret.secretName}')
[ "$SRC" = "app-tls" ]
kubectl -n stor-secvol wait --for=condition=Ready pod/sec-pod --timeout=120s
exit 0

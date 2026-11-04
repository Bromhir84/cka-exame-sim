#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace net-tls86 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n net-tls86 create deploy web --image=nginx:1.27
kubectl -n net-tls86 expose deploy web --port=80
kubectl -n net-tls86 rollout status deploy/web --timeout=120s
# Certificate and key the candidate uses for Secret web-tls.
here="$(cd "$(dirname "$0")" && pwd)"
home="$(dirname "$KUBECONFIG")"
cp "$here/tls.crt" "$home/tls.crt"
cp "$here/tls.key" "$home/tls.key"
chmod 644 "$home/tls.crt" "$home/tls.key"

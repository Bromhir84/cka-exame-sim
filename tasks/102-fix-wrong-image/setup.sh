#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-img102 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-img102 create deploy site --image=nginx:1.27-notreal

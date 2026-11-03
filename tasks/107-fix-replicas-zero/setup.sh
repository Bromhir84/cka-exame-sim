#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-rep107 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-rep107 create deploy web --image=nginx:1.27 --replicas=0

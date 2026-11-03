#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace net-mp90 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n net-mp90 create deploy app --image=nginx:1.27
kubectl -n net-mp90 create deploy api --image=nginx:1.27
kubectl -n net-mp90 expose deploy app --port=80
kubectl -n net-mp90 expose deploy api --port=80
kubectl -n net-mp90 rollout status deploy/app --timeout=120s
kubectl -n net-mp90 rollout status deploy/api --timeout=120s

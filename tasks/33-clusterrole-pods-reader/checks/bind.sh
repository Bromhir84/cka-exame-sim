#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-pods get sa pod-auditor >/dev/null
kubectl -n arch-pods get rolebinding pods-reader-binding >/dev/null
REF=$(kubectl -n arch-pods get rolebinding pods-reader-binding -o jsonpath='{.roleRef.name}')
[ "$REF" = "pods-reader" ]
KIND=$(kubectl -n arch-pods get rolebinding pods-reader-binding -o jsonpath='{.roleRef.kind}')
[ "$KIND" = "ClusterRole" ]
SUB=$(kubectl -n arch-pods get rolebinding pods-reader-binding -o jsonpath='{.subjects[0].name}')
[ "$SUB" = "pod-auditor" ]
exit 0

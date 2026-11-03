#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-cm57 get sa cm-reader >/dev/null
kubectl -n arch-cm57 get rolebinding cm-reader-binding >/dev/null
REF=$(kubectl -n arch-cm57 get rolebinding cm-reader-binding -o jsonpath='{.roleRef.name}')
[ "$REF" = "cm-reader-role" ]
SUB=$(kubectl -n arch-cm57 get rolebinding cm-reader-binding -o jsonpath='{.subjects[0].name}')
[ "$SUB" = "cm-reader" ]
exit 0

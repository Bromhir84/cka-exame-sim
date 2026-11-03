#!/usr/bin/env bash
set -euo pipefail
# empty podSelector is {} 
SEL=$(kubectl -n net-deny get networkpolicy deny-all-ingress -o jsonpath='{.spec.podSelector}')
# ingress should be absent or empty
COUNT=$(kubectl -n net-deny get networkpolicy deny-all-ingress -o json | grep -c '"ingress"' || true)
ING=$(kubectl -n net-deny get networkpolicy deny-all-ingress -o jsonpath='{.spec.ingress[*]}')
[ -z "$ING" ]
exit 0

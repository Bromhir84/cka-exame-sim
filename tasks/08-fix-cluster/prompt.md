# Task 8 — Troubleshoot Cluster DNS (15%)

Cluster DNS is broken. Pods cannot resolve Service names reliably.

Investigate CoreDNS in `kube-system` and restore healthy DNS so that:

- Deployment `coredns` in `kube-system` has Ready replicas matching its desired count
- The CoreDNS ConfigMap is valid (not empty / not sabotaged)

A backup ConfigMap named `coredns-backup` exists in `kube-system` if you need a known-good Corefile.

You may use `kubectl`, logs, and describe. Do not recreate the cluster.

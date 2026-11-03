## Solution
Copy Corefile from ConfigMap `coredns-backup` back to `coredns`, then `kubectl -n kube-system rollout restart deploy/coredns`.

## Goal
SA and Pod both disable service account token automount.

## Steps
```bash
kubectl -n arch-automount apply -f - <<'EOF'
apiVersion: v1
kind: ServiceAccount
metadata:
  name: no-token-sa
  namespace: arch-automount
automountServiceAccountToken: false
---
apiVersion: v1
kind: Pod
metadata:
  name: quiet
  namespace: arch-automount
spec:
  serviceAccountName: no-token-sa
  automountServiceAccountToken: false
  containers:
    - name: busybox
      image: busybox:1.36
      command: ["sleep", "3600"]
EOF
```

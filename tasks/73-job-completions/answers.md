## Goal
Job with 3 completions.

## Steps
```bash
kubectl -n wl-comp73 apply -f - <<'EOF'
apiVersion: batch/v1
kind: Job
metadata:
  name: batch
spec:
  completions: 3
  parallelism: 1
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: c
        image: busybox:1.36
        command: ["sh","-c","echo done"]
EOF
kubectl -n wl-comp73 wait --for=condition=Complete job/batch --timeout=180s
```

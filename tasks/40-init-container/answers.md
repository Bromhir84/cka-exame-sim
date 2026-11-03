## Goal
Pod with initContainer writing to a shared emptyDir, then main container Ready.

## Steps
```bash
kubectl -n wl-init apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: bootstrap
  namespace: wl-init
spec:
  initContainers:
    - name: setup
      image: busybox:1.36
      command: ["sh","-c","echo ready > /work/ok"]
      volumeMounts:
        - name: shared
          mountPath: /work
  containers:
    - name: app
      image: busybox:1.36
      command: ["sh","-c","sleep 3600"]
      volumeMounts:
        - name: shared
          mountPath: /data
  volumes:
    - name: shared
      emptyDir: {}
EOF
```

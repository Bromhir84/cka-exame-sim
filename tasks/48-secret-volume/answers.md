## Goal
Mount Secret `app-tls` at `/var/run/secrets/app`.

## Steps
```bash
kubectl -n stor-secvol create secret generic app-tls --from-literal=token=sekrit
kubectl -n stor-secvol apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: sec-pod
  namespace: stor-secvol
spec:
  containers:
    - name: busybox
      image: busybox:1.36
      command: ["sleep", "3600"]
      volumeMounts:
        - name: tok
          mountPath: /var/run/secrets/app
  volumes:
    - name: tok
      secret:
        secretName: app-tls
EOF
```

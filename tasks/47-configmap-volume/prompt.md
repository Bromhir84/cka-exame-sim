# ConfigMap volume

In namespace `stor-cmvol`:

1. Create ConfigMap `app-files` with key `config.txt` value `hello-cka`
2. Create Pod `cm-pod` (busybox:1.36, `sleep 3600`) mounting that ConfigMap at `/etc/config` (default keys as files)

Pod must be Ready.

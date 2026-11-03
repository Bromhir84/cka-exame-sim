# emptyDir

In namespace `stor-empty` create Pod `cache-pod` that:

- image `busybox:1.36`, command `sleep 3600`
- mounts an **emptyDir** volume named `cache` at `/cache`

Pod must be Ready.

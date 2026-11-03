# ConfigMap envFrom

In namespace `stor-cme98` create ConfigMap `cfg` with `COLOR=blue`. Create Pod `cfg-pod` using `envFrom` configMapRef `cfg` (`busybox:1.36`, sleep). Ready.

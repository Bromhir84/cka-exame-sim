# ServiceAccount imagePullSecrets

In namespace `arch-pull68`:

1. Create Secret `regcred` of type `kubernetes.io/dockerconfigjson` with any valid-looking dockerconfig (dummy is fine)
2. Create ServiceAccount `puller` that references `imagePullSecrets: [{name: regcred}]`

# NetworkPolicy from namespace

In namespace `net-ns88` create NetworkPolicy `allow-from-prod` selecting `app=db` pods, Ingress only, allowing from namespaces labeled `env=prod` (namespaceSelector).

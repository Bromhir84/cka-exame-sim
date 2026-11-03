# Headless Service

Namespace `net-headless` has Deployment `stateful-like` with label `app=store`.

Create Service `store-hs` that is **headless** (`clusterIP: None`), selects `app=store`, port **80** → targetPort **80**.

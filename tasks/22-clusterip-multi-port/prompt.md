# Multi-port Service

Namespace `net-multiport` has Deployment `dual` with labels `app=dual` and containers exposing ports 80 and 8080 (named via container ports).

Create ClusterIP Service `dual-svc` selecting `app=dual` with:

- port name `http`, port **80**, targetPort **80**
- port name `metrics`, port **8080**, targetPort **8080**

# Wrong Service port

Namespace `ts-port` has Deployment `api` exposing container port **8080**, and Service `api-svc` currently listening on port **80** with targetPort **80** (broken).

Fix the Service so port **80** targets **8080**. Keep selector `app=api`.

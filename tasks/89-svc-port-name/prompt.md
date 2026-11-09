# Service targetPort by name

In namespace `net-name89`, create Deployment `api` and ClusterIP Service `named`.

Deployment `api` uses image `nginx:1.27`, label `app=api`, and one container port:

- name `http`
- containerPort **80**

Service `named` selects `app=api` and exposes one port:

- name `http`
- port **80**
- targetPort `http` (the container port's name, not the number 80)

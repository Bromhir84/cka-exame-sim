# ClusterRole — impersonate

Create ClusterRole `user-impersonator` that allows verb `impersonate` on resource `users` in API group empty string.

Create ServiceAccount `impersonator` in `arch-imp67` and ClusterRoleBinding `user-impersonator-binding`.

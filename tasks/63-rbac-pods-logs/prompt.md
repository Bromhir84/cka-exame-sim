# Role — pod logs

In namespace `arch-logs63` create Role `log-reader` allowing `get` on `pods` and `get` on `pods/log`.

Bind it to ServiceAccount `log-reader` via RoleBinding `log-reader-binding`.

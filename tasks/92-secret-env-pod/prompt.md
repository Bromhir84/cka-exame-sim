# Secret env

In namespace `stor-sec92` create Secret `db-creds` with `username=admin` and `password=hunter2`. Create Pod `sec-pod` (`busybox:1.36`, `sleep 3600`) with env `DB_USER` and `DB_PASS` from those keys. Ready.

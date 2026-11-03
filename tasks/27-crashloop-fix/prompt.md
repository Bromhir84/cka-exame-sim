# CrashLoop

Namespace `ts-crash` has Deployment `looper` stuck in CrashLoopBackOff due to a bad command.

Fix it so the container runs `sleep 3600` with image `busybox:1.36` and the Deployment has 1 Ready replica.

Do not delete the Deployment.

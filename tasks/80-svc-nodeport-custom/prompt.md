# NodePort

In namespace `net-np80` create Deployment `web` (`nginx:1.27`, label `app=web`) and Service `web-np` of type NodePort selecting `app=web`, port 80 → targetPort 80, **nodePort 30080**.

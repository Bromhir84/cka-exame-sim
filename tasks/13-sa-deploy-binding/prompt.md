# ServiceAccount on a Deployment

In namespace `arch-sa-deploy`:

1. Create ServiceAccount `app-sa`
2. Create Deployment `sa-demo` with 1 replica, image `nginx:1.27`, container name `web`
3. Set the Pod template `serviceAccountName` to `app-sa`

Ensure the Deployment is Ready.

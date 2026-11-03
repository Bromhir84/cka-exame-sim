## Solution
```bash
kubectl -n broken-app set image deploy/frontend frontend=nginx:1.27
kubectl -n broken-app rollout status deploy/frontend
```

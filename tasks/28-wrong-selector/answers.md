## Solution
`kubectl -n ts-selector patch svc backend-svc -p '{"spec":{"selector":{"app":"backend"}}}'`

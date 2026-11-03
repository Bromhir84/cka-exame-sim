# Pod Pending (taint)

Namespace `ts-taint108` has Pod `critical` Pending because nodes are tainted for the exercise simulation via a **required** nodeAffinity to a missing label—actually: the Pod lacks toleration for taint key `dedicated=cka:NoSchedule` that was applied to the control-plane for this task.

Add an appropriate toleration to the Pod (or recreate it with the same name) so it schedules. Prefer patching/recreating the Pod with toleration `dedicated=cka` effect NoSchedule.

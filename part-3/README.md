### Breaking the app

1. **Failure 1 — OOMKill (Memory)** :  app allocates MEMORY_MB × 1MB at startup. Set MEMORY_MB higher than resources.limits.memory in values.yaml:

```
helm upgrade --install inference-app ./inference-app --set env.MEMORY_MB=300 --set resources.limits.memory=256Mi --wait
```
##### Installing image:
![alt text](image.png)


![alt text](image-1.png)

Describing pod to get events of the pod
![alt text](image-2.png)

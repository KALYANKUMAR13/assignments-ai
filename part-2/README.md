# inference-service

A Helm-based deployment of `inference-service` on a local Minikube cluster, built with production reliability practices.

---

## Why Helm

Helm was chosen over raw YAML or Kustomize for three reasons:

- **Parameterisation** — environment-specific values (replicas, resource sizes, delays) live in `values.yaml` and can be overridden per environment without duplicating manifests.
- **Release management** — `helm upgrade --install` is idempotent, and `helm rollback` gives instant one-command recovery if a release goes bad.
- **Packaging** — the chart is self-contained and portable; anyone can run `make deploy` and get an identical stack.

### Quick Start

```bash
make all        # load image into minikube + deploy helm chart
make forward    # port-forward → http://localhost:8080
make clean      # uninstall helm release
```

 Run all commands from the project root, not inside `inference-app/`


## Image Loading

The image is built locally and loaded into Minikube via tar:

```bash
docker save inference-service:latest -o /tmp/inference-service.tar
minikube image load /tmp/inference-service.tar
```

This is handled automatically by `make all`. If you rebuild the image, re-run `make all` to reload it.

### Horizontal Pod Autoscaler

```yaml
minReplicas: 2
maxReplicas: 5
targetCPUUtilizationPercentage: 60
```

Scaling at 60% leaves 40% headroom so new pods are ready before existing ones saturate. `minReplicas: 2` ensures a single pod failure never causes a full outage.

### Resource Request and Limits:
#### CPU
CPU limits are deliberately omitted. CPU is a compressible resource — when a container exceeds its request, the kernel throttles it rather than killing it. This throttling is silent and shows up as p99 latency spikes rather than errors, making it one of the hardest performance problems to diagnose in Kubernetes.

Setting a CPU limit caps burst capacity for no safety gain. The CPU request is what matters — it guarantees the container gets its share of the node and drives the scheduler's placement decisions. We rely on the HPA to scale out under load rather than artificially throttling pods that could otherwise use available CPU.

#### MEMORY
Memory is non-compressible. A container that exceeds its memory limit is OOMKilled immediately, which is the correct behaviour — a fast restart is better than a pod slowly degrading the node or starving neighbours.

1. **Load testing in staging** — simulate realistic traffic patterns to observe actual CPU and memory consumption under peak load. This gives a measured baseline rather than a guess.

2. **KRR (Kubernetes Resource Recommender)** — run KRR against your cluster after load testing. It analyses historical Prometheus metrics and recommends precise request values per container, removing the guesswork.

3. **VPA (Vertical Pod Autoscaler)**  — VPA can automate resource adjustments but introduces a known problem: it restarts pods to apply new resource values, and pods end up running with different limits at the same time. This makes behaviour inconsistent across replicas and complicates debugging. For this reason VPA is useful in recommendation mode (updateMode: Off) alongside KRR, but not in auto mode for a latency-sensitive inference service.

### PodDisruptionBudget
**PodDisruptionBudget** is a built-in Kubernetes resource — no extra install needed.
It tells Kubernetes to always keep at least 1 pod running for the `inference` app
during voluntary disruptions such as node drains, cluster upgrades, or 
`kubectl delete pod`.


![alt text](image.png)


The below image shows, port-forwarding of svc and the k8s resources likes pods and svc are running with help of helm chart.

![alt text](image-1.png)
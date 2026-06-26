# Incident Postmortem(Sample)

## Trigger

Prometheus alerts were triggered due to elevated latency and increased error rate in the `/predict` endpoint (HighP99Latency and HighErrorRate).

## Impact

Increased latency in `/predict/id` caused customers to experience long wait times while logging into the site. Additionally, another microservice, which depends on this endpoint, became unavailable, resulting in a downstream service disruption.

## Resolution

The issue was traced to simulated latency and forced failures in the `/predict` endpoint. The load conditions were removed, and services returned to normal behavior after stabilization.

## Prevention

Introduce controlled performance testing, improve dependency resilience between microservices, and integrate Alertmanager with Slack for real-time incident visibility in cloud environments.

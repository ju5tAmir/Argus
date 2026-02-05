# IoT Monitoring Stack

Prometheus + Grafana monitoring stack for Raspberry Pi nodes using Node Exporter.

## Architecture

```
┌──────────────────────────────────────┐
│       Central Server (Docker)        │
│                                      │
│  ┌───────────┐    ┌────────────┐     │
│  │  Grafana   │←───│ Prometheus │     │
│  │  :3000     │    │  :9090     │     │
│  └───────────┘    └─────┬──────┘     │
└─────────────────────────┼────────────┘
                          │ scrape every 15s
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
   ┌─────────┐      ┌─────────┐      ┌─────────┐
   │  RPi 1  │      │  RPi 2  │      │  RPi 3  │
   │  Node   │      │  Node   │      │  Node   │
   │ Exporter│      │ Exporter│      │ Exporter│
   │  :9100  │      │  :9100  │      │  :9100  │
   └─────────┘      └─────────┘      └─────────┘
```

## Setup

### 1. Configure RPi Target IPs

Edit `server/prometheus/prometheus.yml` and replace the placeholder IPs with your actual Raspberry Pi IPs:

```yaml
- targets:
    - "192.168.1.101:9100"  # RPi 1
    - "192.168.1.102:9100"  # RPi 2
    - "192.168.1.103:9100"  # RPi 3
```

### 2. Deploy Node Exporter on Each RPi

Copy the `rpi/` directory to each Raspberry Pi and run:

```bash
cd rpi
docker compose up -d
```

### 3. Start the Central Server

On the monitoring server:

```bash
cd server
docker compose up -d
```

## Access

| Service    | URL                          | Credentials   |
|------------|------------------------------|---------------|
| Grafana    | http://\<server-ip\>:3000    | admin / admin |
| Prometheus | http://\<server-ip\>:9090    | -             |

## Pre-configured

- **Dashboard**: Node Exporter Full (ID 1860) - auto-provisioned
- **Datasource**: Prometheus - auto-provisioned
- **Alert Rules** (Grafana unified alerting):
  - **InstanceDown**: fires when a node is unreachable for 1 minute
  - **HighCPU**: fires when CPU usage > 90% for 5 minutes
  - **HighMemory**: fires when memory usage > 85% for 5 minutes
  - **DiskAlmostFull**: fires when disk usage > 85% for 5 minutes

## Verification

1. Check Prometheus targets: `http://<server-ip>:9090/targets`
2. Open Grafana dashboard: Dashboards > Node Exporter Full
3. Check alert rules: Alerting > Alert rules
4. Test alerts: stop a node exporter on an RPi, alert fires after ~1 min

## Adding Notification Channels

Alert notifications are visible in the Grafana UI only. To add Discord or Slack notifications:

1. Go to Grafana > Alerting > Contact points
2. Add a new contact point with your preferred integration
3. Update the notification policy to route alerts to your contact point

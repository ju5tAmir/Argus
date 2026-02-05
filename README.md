# Argus

Prometheus + Grafana + Alertmanager monitoring stack for Raspberry Pi nodes using Node Exporter.

## Architecture

```
┌──────────────────────────────────────────────────┐
│             Central Server (Docker)              │
│                                                  │
│  ┌───────────┐    ┌────────────┐                 │
│  │  Grafana   │←───│ Prometheus │                 │
│  │  :3000     │    │  :9090     │                 │
│  └───────────┘    └──┬──────┬──┘                 │
│                      │      │ alert.rules.yml    │
│                      │  ┌───▼──────────┐         │
│                      │  │ Alertmanager │         │
│                      │  │    :9093     │         │
│                      │  └──────────────┘         │
└──────────────────────┼───────────────────────────┘
                       │ scrape every 15s
       ┌───────────────┼───────────────┐
       ▼               ▼               ▼
  ┌─────────┐    ┌─────────┐    ┌─────────┐
  │  RPi 1  │    │  RPi 2  │    │  RPi 3  │
  │  Node   │    │  Node   │    │  Node   │
  │ Exporter│    │ Exporter│    │ Exporter│
  │  :9100  │    │  :9100  │    │  :9100  │
  └─────────┘    └─────────┘    └─────────┘
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

| Service      | URL                            | Credentials   |
|--------------|--------------------------------|---------------|
| Grafana      | http://\<server-ip\>:3000     | admin / admin |
| Prometheus   | http://\<server-ip\>:9090     | -             |
| Alertmanager | http://\<server-ip\>:9093     | -             |

## Pre-configured

- **Dashboard**: Node Exporter Full (ID 1860) - auto-provisioned
- **Datasource**: Prometheus - auto-provisioned
- **Alert Rules** (Prometheus → Alertmanager):
  - **InstanceDown**: fires when a node is unreachable for 1 minute
  - **HighCPU**: fires when CPU usage > 90% for 5 minutes
  - **HighMemory**: fires when memory usage > 85% for 5 minutes
  - **DiskAlmostFull**: fires when disk usage > 85% for 5 minutes

## Verification

1. Check Prometheus targets: `http://<server-ip>:9090/targets`
2. Check Prometheus alert rules: `http://<server-ip>:9090/alerts`
3. Open Alertmanager UI: `http://<server-ip>:9093`
4. Open Grafana dashboard: Dashboards > Node Exporter Full
5. Test alerts: stop a node exporter on an RPi, InstanceDown fires after ~1 min

## Adding Notification Channels

Alerts are routed through Alertmanager with a default webhook receiver (placeholder). To add real notifications, edit `server/alertmanager/alertmanager.yml`:

- **Discord**: add a `discord_configs` receiver
- **Slack**: add a `slack_configs` receiver
- **Email**: add an `email_configs` receiver

See the [Alertmanager docs](https://prometheus.io/docs/alerting/latest/configuration/) for all receiver types.

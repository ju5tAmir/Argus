# Argus

Prometheus + Grafana + Alertmanager monitoring stack with EFK centralized logging for Raspberry Pi nodes.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Central Server (Docker)                     │
│                                                             │
│  ┌───────────┐    ┌────────────┐    ┌─────────────────┐    │
│  │  Grafana   │←───│ Prometheus │    │ Elasticsearch   │    │
│  │  :3000     │    │  :9090     │    │     :9200       │    │
│  └─────┬─────┘    └──┬──────┬──┘    └──────┬──────────┘    │
│        │             │      │              ▲│              │
│        │             │  ┌───▼──────────┐   │└──┐           │
│        │             │  │ Alertmanager │   │   │           │
│        │             │  │    :9093     │   │ ┌─▼────────┐  │
│        │             │  └──────────────┘   │ │  Kibana  │  │
│        └─────────────┼─────────────────────┘ │  :5601   │  │
│                      │                       └──────────┘  │
└──────────────────────┼──────────────────────────────────────┘
                       │ scrape every 15s        ▲ logs
       ┌───────────────┼───────────────┐         │
       ▼               ▼               ▼         │
  ┌──────────┐   ┌──────────┐   ┌──────────┐    │
  │  RPi 1   │   │  RPi 2   │   │  RPi 3   │    │
  │  Node    │   │  Node    │   │  Node    │    │
  │ Exporter │   │ Exporter │   │ Exporter │    │
  │  :9100   │   │  :9100   │   │  :9100   │    │
  │ Filebeat │   │ Filebeat │   │ Filebeat │────┘
  └──────────┘   └──────────┘   └──────────┘
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

### 2. Start the Central Server

On the monitoring server:

```bash
cd server
docker compose up -d
```

Wait ~60 seconds for Elasticsearch to initialize, then verify:

```bash
curl http://localhost:9200/_cluster/health?pretty
```

### 3. Deploy on Each RPi

Copy the `rpi/` directory to each Raspberry Pi, set the Elasticsearch host, and run:

```bash
cd rpi
ELASTICSEARCH_HOST=http://<server-ip>:9200 docker compose up -d
```

## Access

| Service        | URL                            | Credentials   |
|----------------|--------------------------------|---------------|
| Grafana        | http://\<server-ip\>:3000     | admin / admin |
| Prometheus     | http://\<server-ip\>:9090     | -             |
| Alertmanager   | http://\<server-ip\>:9093     | -             |
| Kibana         | http://\<server-ip\>:5601     | -             |
| Elasticsearch  | http://\<server-ip\>:9200     | -             |

## Pre-configured

- **Dashboard**: Node Exporter Full (ID 1860) - auto-provisioned
- **Datasources**: Prometheus + Elasticsearch - auto-provisioned
- **Alert Rules** (Prometheus -> Alertmanager):
  - **InstanceDown**: fires when a node is unreachable for 1 minute
  - **HighCPU**: fires when CPU usage > 90% for 5 minutes
  - **HighMemory**: fires when memory usage > 85% for 5 minutes
  - **DiskAlmostFull**: fires when disk usage > 85% for 5 minutes
- **Log Collection** (Filebeat -> Elasticsearch):
  - System logs: syslog, auth.log, kern.log
  - Docker container logs with metadata

## Verification

### Metrics

1. Check Prometheus targets: `http://<server-ip>:9090/targets`
2. Check Prometheus alert rules: `http://<server-ip>:9090/alerts`
3. Open Alertmanager UI: `http://<server-ip>:9093`
4. Open Grafana dashboard: Dashboards > Node Exporter Full
5. Test alerts: stop a node exporter on an RPi, InstanceDown fires after ~1 min

### Logs

1. Check Elasticsearch health: `curl http://localhost:9200/_cluster/health?pretty`
2. Check for Filebeat indices: `curl http://localhost:9200/_cat/indices?v`
3. Open Kibana: `http://<server-ip>:5601`
4. Create a data view: Management > Data Views > create `filebeat-*` with `@timestamp`
5. Explore logs: Discover > select `filebeat-*` data view

## Demo Mode

Run everything on a single machine to test without real Raspberry Pis:

```bash
# Start the server stack (includes Elasticsearch + Kibana)
cd server
docker compose up -d

# Start simulated RPi nodes + Filebeat
cd rpi
docker compose -f docker-compose.demo.yml up -d
```

## Adding Notification Channels

Alerts are routed through Alertmanager with a default webhook receiver (placeholder). To add real notifications, edit `server/alertmanager/alertmanager.yml`:

- **Discord**: add a `discord_configs` receiver
- **Slack**: add a `slack_configs` receiver
- **Email**: add an `email_configs` receiver

See the [Alertmanager docs](https://prometheus.io/docs/alerting/latest/configuration/) for all receiver types.

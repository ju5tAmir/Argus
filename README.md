# Argus

Prometheus + Grafana + Alertmanager monitoring stack with EFK centralized logging for Raspberry Pi nodes.

## Architecture

All services communicate via the `argus-network` Docker bridge network. No IP dependencies - works across WiFi network changes.

```
┌─────────────────────────────────────────────────────────────┐
│            Central Server (argus-network)                    │
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
                       │                         ▲
              DNS: rpi-node-1:9100              │ DNS: elasticsearch:9200
                   rpi-node-2:9100              │
                   rpi-node-3:9100              │
                       │                         │
       ┌───────────────┼───────────────┐         │
       ▼               ▼               ▼         │
  ┌──────────┐   ┌──────────┐   ┌──────────┐    │
  │  RPi 1   │   │  RPi 2   │   │  RPi 3   │    │
  │  Node    │   │  Node    │   │  Node    │    │
  │ Exporter │   │ Exporter │   │ Exporter │    │
  │  :9100   │   │  :9100   │   │  :9100   │    │
  │ Filebeat │   │ Filebeat │   │ Filebeat │────┘
  │  Sensors │   │  Sensors │   │  Sensors │
  └──────────┘   └──────────┘   └──────────┘
       ▲               ▲               ▲
       └───────────────┴───────────────┘
            All on argus-network
```

## Setup

### 1. Create Shared Docker Network

On your monitoring server (and each RPi if production deployment):

```bash
docker network create argus-network
```

This creates a Docker bridge network that all services will use for communication.

### 2. Start the Central Server

```bash
cd server
docker compose up -d
```

Wait ~60 seconds for Elasticsearch to initialize, then verify:

```bash
curl http://localhost:9200/_cluster/health?pretty
```

### 3. Deploy on Each RPi (Production)

For production RPi deployments, each RPi needs its own hostname. Edit `server/prometheus/prometheus.yml` to add your RPi hostnames:

```yaml
- job_name: "rpi-nodes"
  static_configs:
    - targets:
        - "rpi-bedroom:9100"
        - "rpi-kitchen:9100"
        - "rpi-garage:9100"
```

Copy the `rpi/` directory to each Raspberry Pi, create the network, and start services:

```bash
# On each RPi
docker network create argus-network
cd rpi
NODE_ID=rpi-bedroom docker compose up -d  # Use unique NODE_ID per device
```

**Network Benefits:**
- ✅ No IP configuration needed - uses Docker DNS (container names)
- ✅ Works across WiFi network changes
- ✅ RPi containers can reach `elasticsearch:9200` directly
- ✅ Prometheus scrapes by container name (e.g., `rpi-node-1:9100`)

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

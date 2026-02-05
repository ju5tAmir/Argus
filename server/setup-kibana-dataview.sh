#!/bin/bash
# Setup Kibana data view for Filebeat logs

KIBANA_URL="http://localhost:5601"

echo "Waiting for Kibana to be ready..."
until curl -s "$KIBANA_URL/api/status" | grep -q '"level":"available"'; do
  echo "Kibana not ready yet, waiting..."
  sleep 5
done

echo "Creating Filebeat data view..."
curl -X POST "$KIBANA_URL/api/data_views/data_view" \
  -H 'kbn-xsrf: true' \
  -H 'Content-Type: application/json' \
  -d '{
    "data_view": {
      "title": "filebeat-*",
      "name": "Filebeat Logs",
      "timeFieldName": "@timestamp"
    }
  }'

echo ""
echo "Data view created! You can now use Discover at $KIBANA_URL/app/discover"

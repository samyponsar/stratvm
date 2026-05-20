#!/bin/bash
set -euo pipefail

API_URL="${API_URL:-http://localhost/api/v1/events}"
API_KEY="${API_KEY:-}"

for i in $(seq 1 1000); do
  if [ -n "$API_KEY" ]; then
    resp=$(curl -sf -X POST "$API_URL" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $API_KEY" \
      -d "{\"tenant_id\":\"acme\",\"event_type\":\"test.event\",\"payload\":{\"iteration\":$i}}")
  else
    resp=$(curl -sf -X POST "$API_URL" \
      -H "Content-Type: application/json" \
      -d "{\"tenant_id\":\"acme\",\"event_type\":\"test.event\",\"payload\":{\"iteration\":$i}}")
  fi

  echo "$resp"
done

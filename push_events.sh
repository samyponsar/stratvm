#!/bin/bash
for i in $(seq 1 10); do
  curl -s -X POST http://localhost:8000/v1/events \
    -H "Content-Type: application/json" \
    -d "{\"tenant_id\":\"t\",\"event_type\":\"test.event\",\"payload\":{\"iteration\":$i}}"
  echo
done

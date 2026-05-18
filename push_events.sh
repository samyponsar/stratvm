#!/bin/bash
for i in $(seq 1 1000); do
  curl -s -X POST http://localhost/api/v1/events \
    -H "Content-Type: application/json" \
    -d "{\"tenant_id\":\"acme\",\"event_type\":\"test.event\",\"payload\":{\"iteration\":$i}}"
  echo
done

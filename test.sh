#!/bin/bash

API_URL="http://localhost:8000/api/v1/events"
TENANTS=("tenant_alpha" "tenant_beta")
EVENT_TYPES=("click" "purchase" "login" "logout" "error" "page_view" "checkout")
TMPDIR=$(mktemp -d)
SUCCESS=0
FAIL=0

cleanup() {
    echo ""
    local elapsed=$(( $(date +%s) - START ))
    local total=$(( SUCCESS + FAIL ))
    echo "Total:      $total"
    echo "Successful: $SUCCESS"
    echo "Failed:     $FAIL"
    echo "Elapsed:    ${elapsed}s"
    [ "$elapsed" -gt 0 ] && echo "Rate:       $((total / elapsed)) events/sec"
    rm -rf "$TMPDIR"
    exit 0
}
trap cleanup INT TERM

START=$(date +%s)
echo "Starting curl stress test at $(date)"
echo "Target: $API_URL"
echo "Press Ctrl+C to stop"
echo ""

while true; do
    for i in $(seq 1 50); do
        tenant=${TENANTS[$((RANDOM % ${#TENANTS[@]}))]}
        etype=${EVENT_TYPES[$((RANDOM % ${#EVENT_TYPES[@]}))]}
        
        curl -s -o /dev/null -w '%{http_code}' \
            -X POST "$API_URL" \
            -H 'Content-Type: application/json' \
            -d "{\"tenant_id\":\"$tenant\",\"event_type\":\"$etype\"}" \
            > "$TMPDIR/$i" &
    done

    for pid in $(jobs -p); do
        wait "$pid"
    done

    for f in "$TMPDIR"/*; do
        code=$(cat "$f" 2>/dev/null)
        [ -z "$code" ] && continue
        if [ "$code" = "200" ]; then
            SUCCESS=$((SUCCESS + 1))
        else
            FAIL=$((FAIL + 1))
        fi
    done
    rm -f "$TMPDIR"/*

    elapsed=$(( $(date +%s) - START ))
    total=$((SUCCESS + FAIL))
    rate=0
    [ "$elapsed" -gt 0 ] && rate=$((total / elapsed))
    echo "  [$total] OK: $SUCCESS | Failed: $FAIL | $rate evt/s | elapsed: ${elapsed}s"
done

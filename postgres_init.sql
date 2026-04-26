CREATE TABLE events (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       VARCHAR(64) NOT NULL,
    event_type      VARCHAR(128) NOT NULL,
    received_at     TIMESTAMPTZ NOT NULL,
    processed_at    TIMESTAMPTZ NOT NULL,
    committed_at    TIMESTAMPTZ NOT NULL,
    success         BOOLEAN NOT NULL,
    failure_reason  TEXT,
    payload         JSONB,
    metadata        JSONB
);

ALTER TABLE events ADD CONSTRAINT chk_failure_reason 
CHECK (success = true OR (success = false AND failure_reason IS NOT NULL));
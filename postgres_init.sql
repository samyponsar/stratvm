CREATE TABLE events (
    id              BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    client_id       VARCHAR(64) NOT NULL,
    event_type      VARCHAR(128) NOT NULL,
    received_at     TIMESTAMPTZ NOT NULL,
    processed_at    TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    success         BOOLEAN NOT NULL,
    failure_reason  TEXT,
    payload         JSONB,
    metadata        JSONB
);

ALTER TABLE events ADD CONSTRAINT chk_failure_reason 
CHECK (success = true OR (success = false AND failure_reason IS NOT NULL));
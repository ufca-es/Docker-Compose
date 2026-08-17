CREATE TABLE IF NOT EXISTS pedidos (
    id BIGSERIAL PRIMARY KEY,
    cliente VARCHAR(120) NOT NULL,
    descricao TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pendente',
    criado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processado_em TIMESTAMPTZ,
    CONSTRAINT pedidos_status_valido
        CHECK (status IN ('pendente', 'processando', 'processado', 'falhou')),
    CONSTRAINT pedidos_processado_em_coerente
        CHECK (status = 'processado' OR processado_em IS NULL)
);

CREATE INDEX IF NOT EXISTS idx_pedidos_status
    ON pedidos (status);

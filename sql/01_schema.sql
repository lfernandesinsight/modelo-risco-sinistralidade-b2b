-- =====================================================================
-- Modelo de Risco de Sinistralidade — Seguradora B2B (dados sintéticos)
-- =====================================================================

-- ---------------------------------------------------------------------
-- DIM_EMPRESA — perfil do cliente (empresa segurada)
-- ---------------------------------------------------------------------
CREATE TABLE dim_empresa (
    empresa_id          VARCHAR(10) PRIMARY KEY,
    razao_social         VARCHAR(150) NOT NULL,
    setor                VARCHAR(50) NOT NULL,
    porte                VARCHAR(20) NOT NULL,       -- MEI, micro, pequena, media, grande
    tempo_mercado_anos   NUMERIC(5,1) NOT NULL,
    estado               CHAR(2) NOT NULL,
    faturamento_anual    NUMERIC(14,2) NOT NULL,
    num_funcionarios     INTEGER NOT NULL
);

CREATE INDEX idx_dim_empresa_setor ON dim_empresa(setor);
CREATE INDEX idx_dim_empresa_porte ON dim_empresa(porte);

-- ---------------------------------------------------------------------
-- FATO_APOLICE — contratos de seguro
-- ---------------------------------------------------------------------
CREATE TABLE fato_apolice (
    apolice_id       VARCHAR(10) PRIMARY KEY,
    empresa_id       VARCHAR(10) NOT NULL REFERENCES dim_empresa(empresa_id),
    cobertura        VARCHAR(30) NOT NULL,   -- responsabilidade_civil, patrimonial, frota, cyber, riscos_operacionais
    valor_segurado   NUMERIC(14,2) NOT NULL,
    premio_anual      NUMERIC(12,2) NOT NULL,
    franquia          NUMERIC(12,2) NOT NULL,
    data_inicio       DATE NOT NULL,
    data_fim          DATE NOT NULL,

    -- coluna alvo do modelo preditivo (calculada após a carga dos sinistros)
    teve_sinistro     BOOLEAN
);

CREATE INDEX idx_fato_apolice_empresa ON fato_apolice(empresa_id);
CREATE INDEX idx_fato_apolice_cobertura ON fato_apolice(cobertura);

-- ---------------------------------------------------------------------
-- FATO_SINISTRO — eventos de sinistro (grão: 1 sinistro)
-- ---------------------------------------------------------------------
CREATE TABLE fato_sinistro (
    sinistro_id       VARCHAR(10) PRIMARY KEY,
    apolice_id        VARCHAR(10) NOT NULL REFERENCES fato_apolice(apolice_id),
    empresa_id        VARCHAR(10) NOT NULL REFERENCES dim_empresa(empresa_id),
    tipo_sinistro     VARCHAR(40) NOT NULL,
    data_sinistro     DATE NOT NULL,
    valor_sinistro    NUMERIC(14,2) NOT NULL,
    status            VARCHAR(15) NOT NULL   -- pago, em_analise, negado
);

CREATE INDEX idx_fato_sinistro_apolice ON fato_sinistro(apolice_id);
CREATE INDEX idx_fato_sinistro_empresa ON fato_sinistro(empresa_id);

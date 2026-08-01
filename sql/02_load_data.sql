-- =====================================================================
-- CARGA — via \copy no psql
-- Rode a partir da raiz do projeto, após gerar os CSVs em data/
-- =====================================================================

\copy dim_empresa(empresa_id, razao_social, setor, porte, tempo_mercado_anos, estado, faturamento_anual, num_funcionarios) FROM 'data/empresas.csv' CSV HEADER;

\copy fato_apolice(apolice_id, empresa_id, cobertura, valor_segurado, premio_anual, franquia, data_inicio, data_fim) FROM 'data/apolices.csv' CSV HEADER;

\copy fato_sinistro(sinistro_id, apolice_id, empresa_id, tipo_sinistro, data_sinistro, valor_sinistro, status) FROM 'data/sinistros.csv' CSV HEADER;

-- =====================================================================
-- Pós-carga: popular a coluna alvo (teve_sinistro) em fato_apolice
-- =====================================================================
UPDATE fato_apolice
SET teve_sinistro = EXISTS (
    SELECT 1 FROM fato_sinistro s WHERE s.apolice_id = fato_apolice.apolice_id
);

-- Conferência rápida
SELECT
    (SELECT COUNT(*) FROM dim_empresa)   AS empresas,
    (SELECT COUNT(*) FROM fato_apolice)  AS apolices,
    (SELECT COUNT(*) FROM fato_sinistro) AS sinistros,
    (SELECT ROUND(100.0 * COUNT(*) FILTER (WHERE teve_sinistro) / COUNT(*), 1) FROM fato_apolice) AS pct_apolices_com_sinistro;

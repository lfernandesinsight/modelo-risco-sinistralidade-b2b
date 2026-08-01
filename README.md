# Modelo de Risco de Sinistralidade — Seguradora B2B

## Sobre o projeto

Modelo preditivo de risco de sinistro para uma seguradora fictícia que atende exclusivamente empresas (B2B) — cobrindo perfil de cliente, apólices e histórico de sinistros, com o objetivo de prever a probabilidade de sinistro por apólice.

> ⚠️ **Importante:** este projeto usa uma **massa de dados sintética, gerada para fins de desenvolvimento e portfólio**. Não existe dataset público adequado de seguros B2B (dado de sinistralidade é informação sensível e raramente aberta pelas seguradoras), então os dados foram simulados com uma lógica de risco plausível — não são dados reais de nenhuma empresa ou seguradora.

## Status

🚧 Em desenvolvimento — Sprint 1 (Geração de dados + modelagem do banco)

## Stack

- Python (geração de dados sintéticos, modelo preditivo)
- PostgreSQL (armazenamento — star schema)
- Grafana (dashboard final)

## Estrutura

```
etl/            script de geração dos dados sintéticos
sql/            DDL e scripts de carga do banco
notebooks/      EDA e desenvolvimento do modelo
dashboard/      configuração/export do Grafana
data/           CSVs gerados (não versionado — reproduzível via etl/gerar_dados_sinteticos.py)
```

## Como reproduzir

1. Instale as dependências: `pip install pandas numpy faker scikit-learn --break-system-packages`
2. Gere os dados: `python etl/gerar_dados_sinteticos.py` (seed fixa — sempre gera o mesmo dataset)
3. Rode os scripts em `sql/` pra criar e popular o banco
4. Abra os notebooks em `notebooks/` pra EDA e modelo

## Roadmap

- [ ] Sprint 1 — Geração de dados sintéticos + modelagem do banco (Postgres)
- [ ] Sprint 2 — Análise exploratória (EDA) + feature engineering
- [ ] Sprint 3 — Modelo preditivo (classificação binária: probabilidade de sinistro)
- [ ] Sprint 4 — Dashboard no Grafana
- [ ] Sprint 5 — Documentação final + publicação no portfólio

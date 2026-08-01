"""
gerar_scores.py

Carrega o modelo treinado (Sprint 3), aplica sobre a base de apólices/empresas
e grava uma tabela de scores de risco no Postgres, para consumo do Grafana
(Sprint 4).

Rodar a partir da raiz do projeto:
    source venv/bin/activate
    python etl/gerar_scores.py
"""

import pandas as pd
import numpy as np
import joblib
from sqlalchemy import create_engine, text

# ---------------------------------------------------------------
# Conexão
# ---------------------------------------------------------------
DB_USER = "postgres"
DB_PASS = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "risco_sinistralidade_dw"

engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# ---------------------------------------------------------------
# Carrega modelo, scaler e lista de features usadas no treino
# ---------------------------------------------------------------
modelo = joblib.load("models/modelo_sinistralidade_logreg.pkl")
scaler = joblib.load("models/scaler.pkl")
features_modelo = joblib.load("models/features_modelo.pkl")

# ---------------------------------------------------------------
# Recarrega o dataset já com as features geradas no Sprint 2
# (mesmo pipeline de feature engineering do notebook 02)
# ---------------------------------------------------------------
df = pd.read_csv("data/dataset_features.csv")

# Garante que as colunas batem exatamente com o treino
# (reindex adiciona colunas faltantes como 0 e ignora extras)
X = df.reindex(columns=features_modelo, fill_value=0)
X_scaled = scaler.transform(X)

# ---------------------------------------------------------------
# Predição — probabilidade de sinistro (score de risco)
# ---------------------------------------------------------------
df["score_risco"] = modelo.predict_proba(X_scaled)[:, 1]

# Classificação em faixas de risco, para facilitar a leitura no dashboard
bins = [0, 0.2, 0.4, 0.6, 0.8, 1.01]
labels = ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"]
df["faixa_risco"] = pd.cut(df["score_risco"], bins=bins, labels=labels, right=False)

# ---------------------------------------------------------------
# Tabela final a gravar: um score por apólice/empresa
# ---------------------------------------------------------------
cols_saida = ["empresa_id", "apolice_id", "score_risco", "faixa_risco"]
cols_saida = [c for c in cols_saida if c in df.columns]

df_scores = df[cols_saida].copy()

print(f"Scores calculados para {len(df_scores)} registros.")
print(df_scores["faixa_risco"].value_counts())

# ---------------------------------------------------------------
# Grava no Postgres (substitui a tabela a cada execução)
# ---------------------------------------------------------------
with engine.begin() as conn:
    conn.execute(text("DROP TABLE IF EXISTS score_risco_empresa"))

df_scores.to_sql("score_risco_empresa", engine, if_exists="replace", index=False)

print("Tabela score_risco_empresa gravada com sucesso no Postgres.")

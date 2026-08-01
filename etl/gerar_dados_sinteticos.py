"""
Geração de dados sintéticos — Seguradora B2B (sinistralidade)
================================================================
ATENÇÃO: Este script gera uma MASSA DE TESTE / DESENVOLVIMENTO.
Não representa dados reais de nenhuma seguradora. A lógica de risco
embutida é uma simplificação plausível, não um modelo atuarial real.

Requer: pip install pandas numpy faker
"""

import numpy as np
import pandas as pd
from faker import Faker
from datetime import timedelta

fake = Faker("pt_BR")
rng = np.random.default_rng(seed=42)  # seed fixa -> dataset reprodutível

N_EMPRESAS = 5000
DATA_REF = pd.Timestamp("2026-01-01")

# ---------------------------------------------------------------------
# 1. EMPRESAS (perfil do cliente)
# ---------------------------------------------------------------------
SETORES = {
    # setor: peso de risco base (multiplicador sobre a prob. de sinistro)
    "construcao_civil":      1.8,
    "transporte_logistica":  1.7,
    "industria":             1.4,
    "comercio_varejo":       1.1,
    "alimenticio":           1.2,
    "saude":                 1.0,
    "tecnologia":            0.6,
    "servicos_financeiros":  0.7,
    "servicos_profissionais":0.65,
    "educacao":              0.75,
}

PORTES = {
    # porte: (peso de risco, faixa de faturamento anual em R$)
    "MEI":      (1.3, (81_000, 360_000)),
    "micro":    (1.25, (360_001, 4_800_000)),
    "pequena":  (1.1, (4_800_001, 20_000_000)),
    "media":    (0.9, (20_000_001, 100_000_000)),
    "grande":   (0.7, (100_000_001, 800_000_000)),
}

ESTADOS = ["SP", "RJ", "MG", "RS", "PR", "SC", "BA", "PE", "CE", "GO", "DF", "AM", "PA", "MA"]

def gerar_empresas(n=N_EMPRESAS):
    setores = rng.choice(list(SETORES.keys()), size=n)
    portes = rng.choice(list(PORTES.keys()), size=n, p=[0.35, 0.30, 0.20, 0.10, 0.05])
    tempo_mercado = rng.gamma(shape=2.0, scale=4.0, size=n).round(1)  # maioria jovem, cauda longa
    tempo_mercado = np.clip(tempo_mercado, 0.2, 60)

    faturamentos = np.array([
        rng.uniform(*PORTES[p][1]) for p in portes
    ]).round(2)

    df = pd.DataFrame({
        "empresa_id": [f"EMP{str(i).zfill(6)}" for i in range(1, n + 1)],
        "razao_social": [fake.company() for _ in range(n)],
        "setor": setores,
        "porte": portes,
        "tempo_mercado_anos": tempo_mercado,
        "estado": rng.choice(ESTADOS, size=n, p=_pesos_estado()),
        "faturamento_anual": faturamentos,
        "num_funcionarios": (faturamentos / rng.uniform(80_000, 200_000, size=n)).astype(int).clip(1, None),
    })
    return df


def _pesos_estado():
    # concentração maior em SP/MG/RJ, parecido com o padrão real de distribuição empresarial no Brasil
    pesos = np.array([0.30, 0.14, 0.10, 0.08, 0.07, 0.05, 0.05, 0.04, 0.04, 0.04, 0.03, 0.02, 0.02, 0.02])
    return pesos / pesos.sum()


# ---------------------------------------------------------------------
# 2. APÓLICES (contratos ativos/históricos por empresa)
# ---------------------------------------------------------------------
COBERTURAS = ["responsabilidade_civil", "patrimonial", "frota", "cyber", "riscos_operacionais"]

def gerar_apolices(empresas_df, min_apolices=1, max_apolices=3):
    registros = []
    apolice_seq = 1
    for _, emp in empresas_df.iterrows():
        n_apolices = rng.integers(min_apolices, max_apolices + 1)
        coberturas_empresa = rng.choice(COBERTURAS, size=n_apolices, replace=False)
        for cobertura in coberturas_empresa:
            valor_segurado = round(emp["faturamento_anual"] * rng.uniform(0.05, 0.35), 2)
            premio_base = valor_segurado * rng.uniform(0.008, 0.025)
            data_inicio = DATA_REF - timedelta(days=int(rng.integers(30, 1460)))
            registros.append({
                "apolice_id": f"APL{str(apolice_seq).zfill(7)}",
                "empresa_id": emp["empresa_id"],
                "cobertura": cobertura,
                "valor_segurado": valor_segurado,
                "premio_anual": round(premio_base, 2),
                "franquia": round(valor_segurado * rng.uniform(0.01, 0.05), 2),
                "data_inicio": data_inicio.date(),
                "data_fim": (data_inicio + timedelta(days=365)).date(),
            })
            apolice_seq += 1
    return pd.DataFrame(registros)


# ---------------------------------------------------------------------
# 3. SINISTROS (histórico de eventos, com lógica de risco embutida)
# ---------------------------------------------------------------------
TIPOS_SINISTRO = {
    "responsabilidade_civil": ["dano_a_terceiro", "processo_trabalhista", "erro_profissional"],
    "patrimonial": ["incendio", "roubo_furto", "alagamento", "dano_estrutural"],
    "frota": ["colisao", "roubo_veiculo", "avaria"],
    "cyber": ["vazamento_dados", "ransomware", "fraude_digital"],
    "riscos_operacionais": ["parada_producao", "acidente_trabalho", "falha_equipamento"],
}

def calcular_prob_sinistro(empresa, apolice):
    """
    Lógica de risco simplificada (não é um modelo atuarial real):
    combina setor, porte, tempo de mercado e tipo de cobertura
    numa probabilidade-base de sinistro no período da apólice.
    """
    base = 0.12  # prob. base de sinistro/ano numa apólice "média"
    peso_setor = SETORES[empresa["setor"]]
    peso_porte = PORTES[empresa["porte"]][0]

    # empresas mais novas no mercado tendem a ter processos menos maduros -> mais risco
    peso_tempo = 1.4 if empresa["tempo_mercado_anos"] < 2 else (
        1.15 if empresa["tempo_mercado_anos"] < 5 else 0.9
    )

    # algumas coberturas têm frequência de sinistro naturalmente maior
    peso_cobertura = {
        "frota": 1.5, "patrimonial": 1.1, "riscos_operacionais": 1.2,
        "cyber": 0.8, "responsabilidade_civil": 0.9,
    }[apolice["cobertura"]]

    prob = base * peso_setor * peso_porte * peso_tempo * peso_cobertura
    return float(np.clip(prob, 0.01, 0.85))


def gerar_sinistros(empresas_df, apolices_df):
    empresas_idx = empresas_df.set_index("empresa_id")
    registros = []
    sinistro_seq = 1

    for _, apolice in apolices_df.iterrows():
        empresa = empresas_idx.loc[apolice["empresa_id"]]
        prob = calcular_prob_sinistro(empresa, apolice)
        ocorreu = rng.random() < prob

        if ocorreu:
            n_sinistros = 1 + rng.poisson(0.3)  # geralmente 1, às vezes mais
            for _ in range(n_sinistros):
                tipo = rng.choice(TIPOS_SINISTRO[apolice["cobertura"]])
                # severidade correlacionada ao valor segurado, com cauda longa (poucos sinistros grandes)
                severidade_pct = rng.beta(a=1.5, b=6)  # concentra em valores baixos, cauda longa
                valor_sinistro = round(apolice["valor_segurado"] * severidade_pct, 2)
                dias_no_periodo = rng.integers(1, 365)
                registros.append({
                    "sinistro_id": f"SIN{str(sinistro_seq).zfill(7)}",
                    "apolice_id": apolice["apolice_id"],
                    "empresa_id": apolice["empresa_id"],
                    "tipo_sinistro": tipo,
                    "data_sinistro": (pd.Timestamp(apolice["data_inicio"]) + timedelta(days=int(dias_no_periodo))).date(),
                    "valor_sinistro": valor_sinistro,
                    "status": rng.choice(["pago", "em_analise", "negado"], p=[0.75, 0.15, 0.10]),
                })
                sinistro_seq += 1

    return pd.DataFrame(registros), None  # segundo retorno reservado (não usado por ora)


if __name__ == "__main__":
    print("Gerando empresas...")
    empresas = gerar_empresas()

    print("Gerando apólices...")
    apolices = gerar_apolices(empresas)

    print("Gerando sinistros (com lógica de risco embutida)...")
    sinistros, _ = gerar_sinistros(empresas, apolices)

    empresas.to_csv("data/empresas.csv", index=False)
    apolices.to_csv("data/apolices.csv", index=False)
    sinistros.to_csv("data/sinistros.csv", index=False)

    print(f"\nEmpresas: {len(empresas)}")
    print(f"Apólices: {len(apolices)}")
    print(f"Sinistros: {len(sinistros)}")
    print(f"Taxa de apólices com sinistro: {sinistros['apolice_id'].nunique() / len(apolices):.1%}")

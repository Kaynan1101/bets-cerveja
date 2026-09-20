"""Gera seeds dbt a partir de conf/metrics.yml e conf/sources.yml."""

from __future__ import annotations

import csv
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
SEEDS = REPO / "transform" / "seeds"


def _write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def export_metricas() -> None:
    payload = yaml.safe_load((REPO / "conf" / "metrics.yml").read_text(encoding="utf-8"))
    rows = [
        {
            "metrica_id": item["id"],
            "unidade": item["unidade"],
            "periodicidade": item["periodicidade"],
            "descricao": item["descricao"],
        }
        for item in payload["metrics"]
    ]
    _write_csv(
        SEEDS / "seed_metricas.csv",
        rows,
        ["metrica_id", "unidade", "periodicidade", "descricao"],
    )


def export_fontes() -> None:
    payload = yaml.safe_load((REPO / "conf" / "sources.yml").read_text(encoding="utf-8"))
    rows = []
    for item in payload["sources"]:
        vintage = item.get("vintage_publicacao")
        ano = item.get("ano_referencia")
        rows.append(
            {
                "source_id": item["id"],
                "vintage_publicacao": int(vintage) if vintage is not None else 0,
                "tier_confiabilidade": item["tier_confiabilidade"],
                "e_oficial": str(bool(item["e_oficial"])).lower(),
                "ano_referencia": "" if ano is None else int(ano),
                "titulo": item["titulo"],
                "dominio": item["dominio"],
                "status_acervo": item.get("status_acervo", ""),
            }
        )
    _write_csv(
        SEEDS / "seed_fontes.csv",
        rows,
        [
            "source_id",
            "vintage_publicacao",
            "tier_confiabilidade",
            "e_oficial",
            "ano_referencia",
            "titulo",
            "dominio",
            "status_acervo",
        ],
    )


CITACOES_FIELDS = [
    "source_id",
    "metrica_id",
    "vintage_publicacao",
    "ano_referencia",
    "periodo",
    "valor",
    "unidade",
    "pagina",
    "citacao_textual",
    "geografia_nivel",
    "geografia_codigo",
    "recorte_classe",
    "recorte_programa",
    "recorte_amostra",
    "categoria_despesa_id",
    "fato",
]


def export_citacoes() -> None:
    rows = [
        {
            "source_id": "strategy_impacto_apostas_consumo_2024",
            "metrica_id": "substituicao_categoria_despesa",
            "vintage_publicacao": 2024,
            "ano_referencia": 2024,
            "periodo": "",
            "valor": 52,
            "unidade": "percentual",
            "pagina": 19,
            "citacao_textual": (
                "Nas classes C, D e E, parte do dinheiro que costumava ser "
                "direcionado para poupança (52% dos respondentes)"
            ),
            "geografia_nivel": "pais",
            "geografia_codigo": "BR",
            "recorte_classe": "C/D/E",
            "recorte_programa": "",
            "recorte_amostra": "",
            "categoria_despesa_id": "poupanca",
            "fato": "substituicao",
        },
        {
            "source_id": "strategy_impacto_apostas_consumo_2024",
            "metrica_id": "substituicao_categoria_despesa",
            "vintage_publicacao": 2024,
            "ano_referencia": 2024,
            "periodo": "",
            "valor": 48,
            "unidade": "percentual",
            "pagina": 19,
            "citacao_textual": (
                "bares, restaurantes e delivery (48% dos respondentes) "
                "são agora usados para as apostas"
            ),
            "geografia_nivel": "pais",
            "geografia_codigo": "BR",
            "recorte_classe": "C/D/E",
            "recorte_programa": "",
            "recorte_amostra": "",
            "categoria_despesa_id": "bares_restaurantes_delivery",
            "fato": "substituicao",
        },
        {
            "source_id": "strategy_impacto_apostas_consumo_2024",
            "metrica_id": "substituicao_categoria_despesa",
            "vintage_publicacao": 2024,
            "ano_referencia": 2024,
            "periodo": "",
            "valor": 43,
            "unidade": "percentual",
            "pagina": 19,
            "citacao_textual": "compras de roupas e acessórios (43% dos respondentes)",
            "geografia_nivel": "pais",
            "geografia_codigo": "BR",
            "recorte_classe": "C/D/E",
            "recorte_programa": "",
            "recorte_amostra": "",
            "categoria_despesa_id": "roupas_acessorios",
            "fato": "substituicao",
        },
        {
            "source_id": "strategy_impacto_apostas_consumo_2024",
            "metrica_id": "substituicao_categoria_despesa",
            "vintage_publicacao": 2024,
            "ano_referencia": 2024,
            "periodo": "",
            "valor": 41,
            "unidade": "percentual",
            "pagina": 19,
            "citacao_textual": (
                "cinemas, teatros e shows (41% dos respondentes), "
                "segundo dados do Instituto Locomotiva."
            ),
            "geografia_nivel": "pais",
            "geografia_codigo": "BR",
            "recorte_classe": "C/D/E",
            "recorte_programa": "",
            "recorte_amostra": "",
            "categoria_despesa_id": "cultura_cinema_teatro_shows",
            "fato": "substituicao",
        },
        {
            "source_id": "bcb_ee119_apostas_2024",
            "metrica_id": "fluxo_bruto_apostado",
            "vintage_publicacao": 2024,
            "ano_referencia": 2024,
            "periodo": "2024-08-01",
            "valor": 20800000000,
            "unidade": "brl",
            "pagina": 2,
            "citacao_textual": (
                "56 empresas que somaram, em agosto, R$ 20,8 bilhões de "
                "transferências recebidas."
            ),
            "geografia_nivel": "pais",
            "geografia_codigo": "BR",
            "recorte_classe": "",
            "recorte_programa": "",
            "recorte_amostra": "",
            "categoria_despesa_id": "",
            "fato": "indicador",
        },
        {
            "source_id": "bcb_ee119_apostas_2024",
            "metrica_id": "fluxo_bruto_apostado",
            "vintage_publicacao": 2024,
            "ano_referencia": 2024,
            "periodo": "2024-08-01",
            "valor": 3000000000,
            "unidade": "brl",
            "pagina": 2,
            "citacao_textual": (
                "5 milhões de pessoas pertencentes a famílias beneficiárias do "
                "Bolsa Família (PBF) enviaram R$ 3 bilhões às empresas de aposta"
            ),
            "geografia_nivel": "pais",
            "geografia_codigo": "BR",
            "recorte_classe": "",
            "recorte_programa": "PBF",
            "recorte_amostra": "",
            "categoria_despesa_id": "",
            "fato": "indicador",
        },
        {
            "source_id": "bcb_ee119_apostas_2024",
            "metrica_id": "apostadores",
            "vintage_publicacao": 2024,
            "ano_referencia": 2024,
            "periodo": "2024-08-01",
            "valor": 5000000,
            "unidade": "pessoas",
            "pagina": 2,
            "citacao_textual": (
                "estima-se que, em agosto de 2024, 5 milhões de pessoas "
                "pertencentes a famílias beneficiárias do Bolsa Família (PBF)"
            ),
            "geografia_nivel": "pais",
            "geografia_codigo": "BR",
            "recorte_classe": "",
            "recorte_programa": "PBF",
            "recorte_amostra": "",
            "categoria_despesa_id": "",
            "fato": "indicador",
        },
        {
            "source_id": "web_valor_klavi_apostadores_2026",
            "metrica_id": "apostadores",
            "vintage_publicacao": 2026,
            "ano_referencia": 2025,
            "periodo": "2025-01-01",
            "valor": 3700000,
            "unidade": "pessoas",
            "pagina": "",
            "citacao_textual": (
                "O número de apostadores brasileiros chegou a 3,7 milhões em 2025, "
                "o dobro do ano anterior. Os dados são da klavi"
            ),
            "geografia_nivel": "pais",
            "geografia_codigo": "BR",
            "recorte_classe": "",
            "recorte_programa": "",
            "recorte_amostra": "open_finance",
            "categoria_despesa_id": "",
            "fato": "indicador",
        },
        {
            "source_id": "ieps_dossie_bets_saude",
            "metrica_id": "empregos_setor_apostas",
            "vintage_publicacao": 2025,
            "ano_referencia": 2024,
            "periodo": "2024-12-01",
            "valor": 1144,
            "unidade": "pessoas",
            "pagina": 31,
            "citacao_textual": (
                "havia apenas 1.144 empregos formais ativos em 31/12/2024 "
                "com 60 empregadores formais."
            ),
            "geografia_nivel": "pais",
            "geografia_codigo": "BR",
            "recorte_classe": "",
            "recorte_programa": "",
            "recorte_amostra": "",
            "categoria_despesa_id": "",
            "fato": "indicador",
        },
        {
            "source_id": "lca_ibjr_anjl_panorama_apostas_2025",
            "metrica_id": "empregos_setor_apostas",
            "vintage_publicacao": 2025,
            "ano_referencia": 2025,
            "periodo": "2025-11-01",
            "valor": 15500,
            "unidade": "pessoas",
            "pagina": 3,
            "citacao_textual": "15,5 mil dos vínculos são de empregos diretos e indiretos",
            "geografia_nivel": "pais",
            "geografia_codigo": "BR",
            "recorte_classe": "",
            "recorte_programa": "",
            "recorte_amostra": "",
            "categoria_despesa_id": "",
            "fato": "indicador",
        },
        {
            "source_id": "anuario_cerveja_ref2023_pub2024",
            "metrica_id": "producao_cerveja_litros",
            "vintage_publicacao": 2024,
            "ano_referencia": 2023,
            "periodo": "2023-01-01",
            "valor": 15361344112.77,
            "unidade": "litro",
            "pagina": 44,
            "citacao_textual": (
                "O volume de produção declarado atinge nacionalmente o montante "
                "de 15.361.344.112,77 litros."
            ),
            "geografia_nivel": "pais",
            "geografia_codigo": "BR",
            "recorte_classe": "",
            "recorte_programa": "",
            "recorte_amostra": "",
            "categoria_despesa_id": "",
            "fato": "mercado_anual",
        },
        {
            "source_id": "anuario_cerveja_ref2024_pub2025",
            "metrica_id": "producao_cerveja_litros",
            "vintage_publicacao": 2025,
            "ano_referencia": 2024,
            "periodo": "2024-01-01",
            "valor": 15344065267.36,
            "unidade": "litro",
            "pagina": 51,
            "citacao_textual": (
                "O volume de produção declarado atinge nacionalmente o montante "
                "de 15.344.065.267,36 litros."
            ),
            "geografia_nivel": "pais",
            "geografia_codigo": "BR",
            "recorte_classe": "",
            "recorte_programa": "",
            "recorte_amostra": "",
            "categoria_despesa_id": "",
            "fato": "mercado_anual",
        },
        {
            "source_id": "anuario_cerveja_ref2025_pub2026",
            "metrica_id": "producao_cerveja_litros",
            "vintage_publicacao": 2026,
            "ano_referencia": 2024,
            "periodo": "2024-01-01",
            "valor": 17210754610.75,
            "unidade": "litro",
            "pagina": 51,
            "citacao_textual": (
                "quando o volume declarado de produção de cerveja foi de "
                "17.210.754.610,75 litros."
            ),
            "geografia_nivel": "pais",
            "geografia_codigo": "BR",
            "recorte_classe": "",
            "recorte_programa": "",
            "recorte_amostra": "",
            "categoria_despesa_id": "",
            "fato": "mercado_anual",
        },
        {
            "source_id": "anuario_cerveja_ref2025_pub2026",
            "metrica_id": "producao_cerveja_litros",
            "vintage_publicacao": 2026,
            "ano_referencia": 2025,
            "periodo": "2025-01-01",
            "valor": 15688083191.69,
            "unidade": "litro",
            "pagina": 51,
            "citacao_textual": (
                "O volume de produção declarado atinge nacionalmente o montante "
                "de 15.688.083.191,69 litros."
            ),
            "geografia_nivel": "pais",
            "geografia_codigo": "BR",
            "recorte_classe": "",
            "recorte_programa": "",
            "recorte_amostra": "",
            "categoria_despesa_id": "",
            "fato": "mercado_anual",
        },
        {
            "source_id": "anuario_cerveja_ref2025_pub2026",
            "metrica_id": "empregos_setor_cerveja",
            "vintage_publicacao": 2026,
            "ano_referencia": 2025,
            "periodo": "2025-01-01",
            "valor": 41305,
            "unidade": "pessoas",
            "pagina": 45,
            "citacao_textual": (
                "Fabricação de Cerveja e Chopes 41.305 (-2.72%). "
                "Somente os dados oficiais do governo federal em relação aos empregos diretos."
            ),
            "geografia_nivel": "pais",
            "geografia_codigo": "BR",
            "recorte_classe": "",
            "recorte_programa": "",
            "recorte_amostra": "",
            "categoria_despesa_id": "",
            "fato": "indicador",
        },
    ]
    _write_csv(SEEDS / "seed_citacoes.csv", rows, CITACOES_FIELDS)


if __name__ == "__main__":
    export_metricas()
    export_fontes()
    export_citacoes()
    print(f"escreveu {SEEDS / 'seed_metricas.csv'}")
    print(f"escreveu {SEEDS / 'seed_fontes.csv'}")
    print(f"escreveu {SEEDS / 'seed_citacoes.csv'}")

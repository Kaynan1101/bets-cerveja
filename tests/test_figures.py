from __future__ import annotations

import duckdb
import pandas as pd

from betscerveja.figures import REQUIRED_ARTIFACTS, render_figures


def _seed_warehouse(path) -> None:
    panorama = pd.DataFrame(
        {
            "data_inicio": pd.date_range("2023-01-01", periods=4, freq="MS"),
            "producao_bebidas_alcoolicas_indice": [100.0, 101.0, 99.5, 102.0],
            "producao_industrial_geral_indice": [100.0, 100.5, 101.0, 101.2],
            "ipca_cerveja": [110.0, 111.0, 112.0, 113.0],
            "rendimento_real": [2800.0, 2810.0, 2820.0, 2830.0],
        }
    )
    anual = pd.DataFrame(
        {
            "ano_referencia": [2023, 2024, 2024, 2025],
            "vintage_publicacao": [2024, 2025, 2026, 2026],
            "geografia_id": ["pais|BR"] * 4,
            "source_id": ["a", "b", "c", "c"],
            "metrica_id": ["producao_cerveja_litros"] * 4,
            "data_inicio": pd.to_datetime(["2023-01-01", "2024-01-01", "2024-01-01", "2025-01-01"]),
            "valor": [1.5e10, 1.53e10, 1.72e10, 1.57e10],
            "unidade": ["litro"] * 4,
            "pagina": [44, 51, 51, 51],
            "citacao_textual": ["x"] * 4,
            "granularidade_periodo": ["ano"] * 4,
        }
    )
    previsao = pd.DataFrame(
        {
            "data_inicio": pd.date_range("2023-01-01", periods=4, freq="MS"),
            "realizado": [100.0, 101.0, 99.5, 102.0],
            "previsto": [100.2, 100.8, 100.1, 101.5],
            "ic_inf": [98.0, 98.5, 97.8, 99.0],
            "ic_sup": [102.5, 103.0, 102.4, 104.0],
            "dentro_do_intervalo": [True, True, True, True],
        }
    )
    substituicao = pd.DataFrame(
        {
            "categoria_id": [
                "poupanca",
                "bares_restaurantes_delivery",
                "roupas_acessorios",
                "cultura_cinema_teatro_shows",
            ],
            "recorte_id": ["cde"] * 4,
            "source_id": ["strategy_impacto_apostas_consumo_2024"] * 4,
            "vintage_publicacao": [2024] * 4,
            "metrica_id": ["substituicao_categoria_despesa"] * 4,
            "geografia_id": ["pais|BR"] * 4,
            "data_inicio": pd.to_datetime(["2024-01-01"] * 4),
            "valor": [52.0, 48.0, 43.0, 41.0],
            "unidade": ["percentual"] * 4,
            "pagina": [19] * 4,
            "citacao_textual": ["Locomotiva p. 19"] * 4,
        }
    )
    estrutura = pd.DataFrame(
        {
            "setor": ["apostas_formais", "apostas_diretos_indiretos", "cerveja_fabricacao"],
            "metrica_id": [
                "empregos_setor_apostas",
                "empregos_setor_apostas",
                "empregos_setor_cerveja",
            ],
            "source_id": [
                "ieps_dossie_bets_saude",
                "lca_ibjr_anjl_panorama_apostas_2025",
                "anuario_cerveja_ref2025_pub2026",
            ],
            "vintage_publicacao": [2025, 2025, 2026],
            "data_inicio": pd.to_datetime(["2024-12-01", "2025-11-01", "2025-01-01"]),
            "valor": [1144.0, 15500.0, 41305.0],
            "unidade": ["pessoas"] * 3,
            "pagina": [31, 3, 45],
            "citacao_textual": ["ieps", "ibjr", "caged"],
        }
    )
    divergencias = pd.DataFrame(
        {
            "metrica_id": ["empregos_setor_apostas", "producao_cerveja_litros", "apostadores"],
            "ano_referencia": [2025, 2024, 2025],
            "data_inicio": pd.to_datetime(["2025-01-01", "2024-01-01", "2025-01-01"]),
            "source_id_a": [
                "ieps_dossie_bets_saude",
                "anuario_a",
                "web_valor_klavi_apostadores_2026",
            ],
            "vintage_a": [2025, 2025, 2026],
            "valor_a": [1144.0, 1.53e10, 3700000.0],
            "unidade_a": ["pessoas", "litro", "pessoas"],
            "source_id_b": [
                "lca_ibjr_anjl_panorama_apostas_2025",
                "anuario_b",
                "web_senado_mercado_global_bets_2026",
            ],
            "vintage_b": [2025, 2026, 2026],
            "valor_b": [15500.0, 1.72e10, 25000000.0],
            "unidade_b": ["pessoas", "litro", "pessoas"],
            "tipo_divergencia": ["definicao", "vintage", "amostra_vs_universo"],
            "nota": [
                "IEPS 1.144 vs IBJR/ANJL 15,5 mil. Duas definições, não um número.",
                "Produção 2024 em dois vintages.",
                "Klavi 3,7 mi vs Rádio Senado 25 mi. Amostra ≠ censo.",
            ],
        }
    )
    proveniencia = pd.DataFrame(
        {
            "source_id": [
                "strategy_impacto_apostas_consumo_2024",
                "bcb_ee119_apostas_2024",
                "bcb_ee119_apostas_2024",
                "bcb_ee119_apostas_2024",
                "web_valor_klavi_apostadores_2026",
                "strategy_impacto_apostas_consumo_2024",
                "strategy_impacto_apostas_consumo_2024",
                "strategy_impacto_apostas_consumo_2024",
                "strategy_impacto_apostas_consumo_2024",
                "strategy_impacto_apostas_consumo_2024",
                "strategy_impacto_apostas_consumo_2024",
                "fundaj_nt39_pce_2024",
                "fundaj_nt39_pce_2024",
                "fundaj_nt39_pce_2024",
            ],
            "vintage_publicacao": [2024] * 14,
            "metrica_id": [
                "substituicao_categoria_despesa",
                "fluxo_bruto_apostado",
                "fluxo_bruto_apostado",
                "apostadores",
                "apostadores",
                "participacao_orcamento_apostas",
                "participacao_orcamento_apostas",
                "razao_apostas_alimentacao",
                "razao_apostas_alimentacao",
                "razao_apostas_lazer",
                "razao_apostas_lazer",
                "participacao_orcamento_apostas",
                "pce_bolsa_familia",
                "pce_bolsa_familia",
            ],
            "data_inicio": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-08-01",
                    "2024-08-01",
                    "2024-08-01",
                    "2025-01-01",
                    "2023-01-01",
                    "2023-01-01",
                    "2018-01-01",
                    "2023-01-01",
                    "2018-01-01",
                    "2023-01-01",
                    "2024-08-01",
                    "2024-08-01",
                    "2024-08-01",
                ]
            ),
            "geografia_id": ["pais|BR"] * 14,
            "recorte_id": [
                "cde",
                "br",
                "pbf",
                "pbf",
                "of",
                "br",
                "de",
                "br",
                "br",
                "br",
                "br",
                "pbf",
                "pbf",
                "pbf_med",
            ],
            "pagina": [19, 2, 2, 2, None, 5, 5, 5, 5, 5, 5, 4, 4, 4],
            "citacao_textual": [
                "bares, restaurantes e delivery (48%)",
                "56 empresas que somaram, em agosto, R$ 20,8 bilhões",
                "5 milhões de pessoas pertencentes a famílias beneficiárias do Bolsa Família (PBF)",
                "5 milhões de pessoas pertencentes a famílias beneficiárias do Bolsa Família (PBF)",
                "3,7 milhões em 2025, o dobro do ano anterior",
                "No orçamento médio familiar, elas representavam 0,73% em 2023",
                "As apostas já representam 1,38% do orçamento familiar nas classes D/E",
                "4,9% do que é gasto em alimentação (1,5% em 2018)",
                "4,9% do que é gasto em alimentação (1,5% em 2018)",
                "36% em lazer e cultura (10% em 2018)",
                "36% em lazer e cultura (10% em 2018)",
                "já comprometeria 16,7% do valor do benefício",
                "reduzindo seu PCE de 1,0 para aproximadamente 0,83",
                "reduzindo seu PCE de 1,0 para aproximadamente 0,83",
            ],
            "valor": [
                48.0,
                20800000000.0,
                3000000000.0,
                5000000.0,
                3700000.0,
                0.73,
                1.38,
                1.5,
                4.9,
                10.0,
                36.0,
                16.7,
                1.0,
                0.83,
            ],
            "unidade": [
                "percentual",
                "brl",
                "brl",
                "pessoas",
                "pessoas",
                "percentual",
                "percentual",
                "percentual",
                "percentual",
                "percentual",
                "percentual",
                "percentual",
                "indice",
                "indice",
            ],
            "granularidade_periodo": ["corte"] * 14,
        }
    )

    con = duckdb.connect(str(path))
    con.execute("create schema marts_analytics")
    con.execute("create schema marts_core")
    con.execute("create schema marts_ml")
    con.register("_panorama", panorama)
    con.execute("create table marts_analytics.agg_panorama_mensal as select * from _panorama")
    con.register("_anual", anual)
    con.execute("create table marts_core.fct_mercado_cerveja_anual as select * from _anual")
    con.register("_prev", previsao)
    con.execute("create table marts_ml.fct_cerveja_previsao as select * from _prev")
    con.register("_sub", substituicao)
    con.execute("create table marts_analytics.agg_de_onde_saiu_o_dinheiro as select * from _sub")
    con.register("_est", estrutura)
    con.execute("create table marts_analytics.agg_estrutura_setorial as select * from _est")
    con.register("_div", divergencias)
    con.execute("create table marts_analytics.qa_divergencias as select * from _div")
    con.register("_prov", proveniencia)
    con.execute("create table marts_analytics.agg_indicadores_declarados as select * from _prov")
    con.close()


def test_render_figures_grava_png_e_html(tmp_path) -> None:
    db = tmp_path / "betscerveja.duckdb"
    out = tmp_path / "figures"
    _seed_warehouse(db)

    summary = render_figures(duckdb_file=db, output_dir=out)

    assert summary["output_dir"] == str(out)
    for name in REQUIRED_ARTIFACTS:
        assert (out / name).is_file()
    mix = list(out.glob("*mix*")) + list(out.glob("*malte*")) + list(out.glob("*alcool*"))
    assert mix == []
    html = (out / "index.html").read_text(encoding="utf-8")
    assert "agg_indicadores_declarados" in html
    assert "qa_divergencias" in html
    assert "48" in html
    assert "ato2_pix_ee119.png" in html
    assert "ato2_apostadores.png" in html
    assert "ato1_renda.png" in html
    assert "ato2_orcamento.png" in html
    assert "plotly" not in html.lower()
    assert "<script" not in html.lower()

"""Lê o warehouse DuckDB e grava PNG + HTML em exports/figures/."""

from __future__ import annotations

import html
from pathlib import Path

import duckdb
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd

from betscerveja.models.sarimax import duckdb_path
from betscerveja.registry import REPO_ROOT

DEFAULT_OUTPUT = REPO_ROOT / "exports" / "figures"

REQUIRED_ARTIFACTS: tuple[str, ...] = (
    "ato1_panorama.png",
    "ato1_producao_anual.png",
    "ato1_sarimax.png",
    "ato2_substituicao.png",
    "ato3_emprego.png",
    "index.html",
)

CATEGORIA_NOMES = {
    "poupanca": "Poupança",
    "bares_restaurantes_delivery": "Bares, restaurantes e delivery",
    "roupas_acessorios": "Roupas e acessórios",
    "cultura_cinema_teatro_shows": "Cinemas, teatros e shows",
}

EMPREGO_APOSTAS_ROTULO = {
    "ieps_dossie_bets_saude": "IEPS — formais\n(31/12/2024)",
    "lca_ibjr_anjl_panorama_apostas_2025": "IBJR/ANJL — diretos e indiretos\n(nov/2025)",
}


def render_figures(
    duckdb_file: Path | str | None = None,
    output_dir: Path | str | None = None,
) -> dict[str, str]:
    """Abre o DuckDB (somente leitura) e escreve os artefatos da etapa 9."""
    db_path = duckdb_path(duckdb_file)
    if not db_path.exists():
        raise FileNotFoundError(f"DuckDB não encontrado: {db_path}")

    dest = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT
    dest.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(db_path), read_only=True)
    try:
        if not _table_exists(con, "fct_cerveja_previsao"):
            raise FileNotFoundError(
                "fct_cerveja_previsao não existe. Execute a etapa 8 (`make sarimax`) antes."
            )
        panorama = _read_table(con, "agg_panorama_mensal")
        anual = _read_table(con, "fct_mercado_cerveja_anual")
        previsao = _read_table(con, "fct_cerveja_previsao")
        substituicao = _read_table(con, "agg_de_onde_saiu_o_dinheiro")
        estrutura = _read_table(con, "agg_estrutura_setorial")
        divergencias = _read_table(con, "qa_divergencias")
        proveniencia = _read_table(con, "agg_indicadores_declarados")
    finally:
        con.close()

    _plot_panorama(panorama, dest / "ato1_panorama.png")
    _plot_producao_anual(anual, dest / "ato1_producao_anual.png")
    _plot_sarimax(previsao, dest / "ato1_sarimax.png")
    _plot_substituicao(substituicao, dest / "ato2_substituicao.png")
    _plot_emprego(estrutura, divergencias, dest / "ato3_emprego.png")
    _write_index(dest, proveniencia, divergencias)

    return {
        "duckdb": str(db_path),
        "output_dir": str(dest),
        "artifacts": ", ".join(REQUIRED_ARTIFACTS),
    }


def _table_exists(con: duckdb.DuckDBPyConnection, name: str) -> bool:
    row = con.execute(
        """
        select 1
        from information_schema.tables
        where lower(table_name) = lower(?)
        limit 1
        """,
        [name],
    ).fetchone()
    return row is not None


def _schema_for(con: duckdb.DuckDBPyConnection, name: str) -> str:
    found = con.execute(
        """
        select table_schema
        from information_schema.tables
        where lower(table_name) = lower(?)
        order by case when table_schema like '%marts%' then 0 else 1 end
        limit 1
        """,
        [name],
    ).fetchone()
    if not found:
        raise FileNotFoundError(f"tabela não encontrada no DuckDB: {name}")
    return found[0]


def _read_table(con: duckdb.DuckDBPyConnection, name: str) -> pd.DataFrame:
    schema = _schema_for(con, name)
    return con.execute(f'select * from "{schema}"."{name}"').fetchdf()


def _save(fig: plt.Figure, path: Path) -> None:
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)


def _plot_panorama(frame: pd.DataFrame, path: Path) -> None:
    if frame.empty:
        raise ValueError("agg_panorama_mensal está vazio")
    data = frame.copy()
    data["data_inicio"] = pd.to_datetime(data["data_inicio"])
    data = data.sort_values("data_inicio")

    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    ax_idx, ax_ipca = axes

    ax_idx.plot(
        data["data_inicio"],
        data["producao_bebidas_alcoolicas_indice"],
        color="#1f4e79",
        linewidth=2,
        label="SIDRA 8885 11.1 (bebidas alcoólicas)",
    )
    if data["producao_industrial_geral_indice"].notna().any():
        ax_idx.plot(
            data["data_inicio"],
            data["producao_industrial_geral_indice"],
            color="#7a7a7a",
            linewidth=1.4,
            linestyle="--",
            label="PIM geral (contexto)",
        )
    ax_idx.set_ylabel("Índice de produção")
    ax_idx.set_title("Ato 1 — Panorama mensal (índices de produção)")
    ax_idx.legend(loc="best", fontsize=8)
    ax_idx.grid(True, alpha=0.3)

    ax_ipca.plot(
        data["data_inicio"],
        data["ipca_cerveja"],
        color="#c45c26",
        linewidth=1.6,
        label="IPCA cerveja (eixo próprio)",
    )
    ax_ipca.set_ylabel("IPCA cerveja")
    ax_ipca.set_xlabel("Mês")
    ax_ipca.set_title("Contexto de preço — não misturado ao índice de produção")
    ax_ipca.legend(loc="best", fontsize=8)
    ax_ipca.grid(True, alpha=0.3)
    fig.tight_layout()
    _save(fig, path)


def _plot_producao_anual(frame: pd.DataFrame, path: Path) -> None:
    if frame.empty:
        raise ValueError("fct_mercado_cerveja_anual está vazio")
    data = frame.copy()
    data = data[data["metrica_id"] == "producao_cerveja_litros"]
    if data.empty:
        raise ValueError("fct_mercado_cerveja_anual sem producao_cerveja_litros")
    data["bilhoes_l"] = data["valor"] / 1e9
    data = data.sort_values(["ano_referencia", "vintage_publicacao"])
    data["rotulo"] = [
        f"{int(ano)}\n(vintage {int(vin)})"
        for ano, vin in zip(data["ano_referencia"], data["vintage_publicacao"], strict=True)
    ]

    n_2024 = int((data["ano_referencia"] == 2024).sum())
    if n_2024 < 2:
        raise ValueError("produção anual precisa dos dois vintages de 2024")

    fig, ax = plt.subplots(figsize=(9, 5))
    cores = ["#1f4e79" if ano != 2024 else "#c45c26" for ano in data["ano_referencia"]]
    ax.bar(range(len(data)), data["bilhoes_l"], color=cores, width=0.65)
    ax.set_xticks(range(len(data)), data["rotulo"])
    ax.set_ylabel("Bilhões de litros")
    ax.set_title("Ato 1 — Produção anual MAPA (2024 em dois vintages, sem média)")
    for i, valor in enumerate(data["bilhoes_l"]):
        ax.text(i, valor, f"{valor:.2f}", ha="center", va="bottom", fontsize=8)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    _save(fig, path)


def _plot_sarimax(frame: pd.DataFrame, path: Path) -> None:
    if frame.empty:
        raise ValueError("fct_cerveja_previsao está vazio")
    data = frame.copy()
    data["data_inicio"] = pd.to_datetime(data["data_inicio"])
    data = data.sort_values("data_inicio")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.fill_between(
        data["data_inicio"],
        data["ic_inf"],
        data["ic_sup"],
        color="#1f4e79",
        alpha=0.22,
        label="IC 95%",
    )
    ax.plot(
        data["data_inicio"],
        data["previsto"],
        color="#1f4e79",
        linestyle="--",
        linewidth=1.6,
        label="Previsto",
    )
    ax.plot(
        data["data_inicio"],
        data["realizado"],
        color="#222222",
        linewidth=2,
        label="Realizado",
    )
    ax.set_title("Ato 1 — Contrafactual SARIMAX (realizado, previsto, IC 95%)")
    ax.set_ylabel("Índice SIDRA 8885 11.1")
    ax.set_xlabel("Mês")
    ax.legend(loc="best", fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    _save(fig, path)


def _plot_substituicao(frame: pd.DataFrame, path: Path) -> None:
    if frame.empty:
        raise ValueError("agg_de_onde_saiu_o_dinheiro está vazio")
    data = frame.copy()
    data["nome"] = data["categoria_id"].map(CATEGORIA_NOMES).fillna(data["categoria_id"])
    data = data.sort_values("valor", ascending=True)

    cores = [
        "#c45c26" if cat == "bares_restaurantes_delivery" else "#1f4e79"
        for cat in data["categoria_id"]
    ]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(data["nome"], data["valor"], color=cores)
    ax.set_xlabel("% dos respondentes (classes C/D/E)")
    ax.set_title("Ato 2 — De onde saiu o dinheiro (Locomotiva p. 19)")
    for y, valor in enumerate(data["valor"]):
        ax.text(valor, y, f" {valor:.0f}%", va="center", fontsize=9)
    ax.grid(True, axis="x", alpha=0.3)
    fig.tight_layout()
    _save(fig, path)


def _plot_emprego(estrutura: pd.DataFrame, divergencias: pd.DataFrame, path: Path) -> None:
    if estrutura.empty:
        raise ValueError("agg_estrutura_setorial está vazio")
    apostas = estrutura[estrutura["metrica_id"] == "empregos_setor_apostas"].copy()
    if len(apostas) < 2:
        raise ValueError("emprego de apostas precisa de IEPS e IBJR, sem média")
    apostas["rotulo"] = apostas["source_id"].map(EMPREGO_APOSTAS_ROTULO)
    apostas["rotulo"] = apostas["rotulo"].fillna(apostas["source_id"])
    apostas = apostas.sort_values("valor")

    nota = ""
    emprego_div = divergencias[divergencias["metrica_id"] == "empregos_setor_apostas"]
    if not emprego_div.empty and "nota" in emprego_div.columns:
        nota = str(emprego_div["nota"].iloc[0])

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(apostas["rotulo"], apostas["valor"], color=["#1f4e79", "#c45c26"])
    ax.set_xlabel("Pessoas (definições distintas — não é série)")
    ax.set_title("Ato 3 — Emprego em apostas: dois números rotulados")
    for y, valor in enumerate(apostas["valor"]):
        ax.text(valor, y, f" {valor:,.0f}".replace(",", "."), va="center", fontsize=9)
    if nota:
        ax.text(0.0, -0.28, nota, transform=ax.transAxes, fontsize=7, wrap=True)
    cerveja = estrutura[estrutura["metrica_id"] == "empregos_setor_cerveja"]
    if not cerveja.empty:
        n = float(cerveja["valor"].iloc[0])
        ax.text(
            0.99,
            0.05,
            f"Cerveja (CAGED, Anuário): {n:,.0f} empregos".replace(",", "."),
            transform=ax.transAxes,
            ha="right",
            fontsize=8,
            color="#444444",
        )
    ax.grid(True, axis="x", alpha=0.3)
    fig.tight_layout()
    _save(fig, path)


def _write_index(dest: Path, proveniencia: pd.DataFrame, divergencias: pd.DataFrame) -> None:
    figuras = (
        ("ato1_panorama.png", "Ato 1 — Panorama mensal (SIDRA 8885 11.1)"),
        ("ato1_producao_anual.png", "Ato 1 — Produção anual MAPA (dois vintages de 2024)"),
        ("ato1_sarimax.png", "Ato 1 — Contrafactual SARIMAX"),
        ("ato2_substituicao.png", "Ato 2 — Substituição declarada (Locomotiva p. 19)"),
        ("ato3_emprego.png", "Ato 3 — Emprego IEPS vs IBJR"),
    )
    blocos = []
    for arquivo, titulo in figuras:
        blocos.append(
            f"<section><h2>{html.escape(titulo)}</h2>"
            f'<p><img src="{html.escape(arquivo)}" alt="{html.escape(titulo)}"></p></section>'
        )
    page = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>Figuras — bets-cerveja</title>
  <style>
    body {{
      font-family: Georgia, serif; max-width: 960px;
      margin: 2rem auto; padding: 0 1rem; color: #222;
    }}
    img {{ max-width: 100%; height: auto; }}
    table {{
      border-collapse: collapse; width: 100%;
      font-size: 0.85rem; margin-bottom: 2rem;
    }}
    th, td {{
      border: 1px solid #ccc; padding: 0.35rem 0.5rem;
      text-align: left; vertical-align: top;
    }}
    th {{ background: #f3f3f3; }}
    .nota {{ color: #555; font-size: 0.9rem; }}
  </style>
</head>
<body>
  <h1>Figuras estáticas</h1>
  <p class="nota">Geradas a partir do DuckDB.
  Mix de produto (sem álcool / puro malte) não entra no gráfico.
  Sem JavaScript de charting. Catálogo dbt continua no GitHub Pages.</p>
  {"".join(blocos)}
  <section>
    <h2>Proveniência (<code>agg_indicadores_declarados</code>)</h2>
    {_df_html(proveniencia)}
  </section>
  <section>
    <h2>Divergências (<code>qa_divergencias</code>)</h2>
    {_df_html(divergencias)}
  </section>
</body>
</html>
"""
    (dest / "index.html").write_text(page, encoding="utf-8")


def _df_html(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "<p>Tabela vazia.</p>"
    shown = frame.copy()
    for col in shown.columns:
        if pd.api.types.is_datetime64_any_dtype(shown[col]):
            shown[col] = pd.to_datetime(shown[col]).dt.strftime("%Y-%m-%d")
    header = "".join(f"<th>{html.escape(str(col))}</th>" for col in shown.columns)
    rows = []
    for rec in shown.itertuples(index=False):
        cells = "".join(f"<td>{html.escape('' if pd.isna(v) else str(v))}</td>" for v in rec)
        rows.append(f"<tr>{cells}</tr>")
    return f"<table><thead><tr>{header}</tr></thead><tbody>{''.join(rows)}</tbody></table>"

"""Empacota só derivado (marts + figuras + atribuição) em exports/zenodo/."""

from __future__ import annotations

import shutil
from pathlib import Path

import duckdb

from betscerveja.figures.render import DEFAULT_OUTPUT as DEFAULT_FIGURES
from betscerveja.figures.render import REQUIRED_ARTIFACTS, _read_table, _table_exists
from betscerveja.models.sarimax import duckdb_path
from betscerveja.registry import REPO_ROOT

DEFAULT_OUTPUT = REPO_ROOT / "exports" / "zenodo"
DOI_PLACEHOLDER = "https://doi.org/10.5281/zenodo.XXXX"
REPO_URL = "https://github.com/Kaynan1101/bets-cerveja"

ZENODO_MARTS: tuple[str, ...] = (
    "agg_panorama_mensal",
    "fct_mercado_cerveja_anual",
    "fct_cerveja_previsao",
    "agg_de_onde_saiu_o_dinheiro",
    "agg_estrutura_setorial",
    "qa_divergencias",
    "agg_indicadores_declarados",
    "ml_metricas",
    "ml_coeficientes",
)


def pack_zenodo(
    duckdb_file: Path | str | None = None,
    figures_dir: Path | str | None = None,
    output_dir: Path | str | None = None,
) -> dict[str, str]:
    """Escreve o pacote Zenodo. Sem DuckDB, sem .env, sem lake, sem 00_landing."""
    db_path = duckdb_path(duckdb_file)
    if not db_path.exists():
        raise FileNotFoundError(f"DuckDB não encontrado: {db_path}")

    src_figures = Path(figures_dir) if figures_dir is not None else DEFAULT_FIGURES
    dest = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT
    dest.mkdir(parents=True, exist_ok=True)

    marts_dir = dest / "marts"
    figures_out = dest / "figures"
    if marts_dir.exists():
        shutil.rmtree(marts_dir)
    if figures_out.exists():
        shutil.rmtree(figures_out)
    marts_dir.mkdir()
    figures_out.mkdir()

    written: list[str] = []
    con = duckdb.connect(str(db_path), read_only=True)
    try:
        for name in ZENODO_MARTS:
            if not _table_exists(con, name):
                raise FileNotFoundError(f"tabela não encontrada no DuckDB: {name}")
            frame = _read_table(con, name)
            parquet = marts_dir / f"{name}.parquet"
            frame.to_parquet(parquet, index=False)
            written.append(parquet.relative_to(dest).as_posix())
    finally:
        con.close()

    for name in REQUIRED_ARTIFACTS:
        src = src_figures / name
        if not src.is_file():
            raise FileNotFoundError(f"figura não encontrada: {src}")
        target = figures_out / name
        shutil.copy2(src, target)
        written.append(target.relative_to(dest).as_posix())

    for filename in ("LICENSE-DATA", "CITATION.cff", ".zenodo.json"):
        src = REPO_ROOT / filename
        if not src.is_file():
            raise FileNotFoundError(f"metadado não encontrado: {src}")
        target = dest / filename
        shutil.copy2(src, target)
        written.append(filename)

    readme = dest / "README.md"
    readme.write_text(_package_readme(), encoding="utf-8")
    written.append("README.md")

    manifest = dest / "MANIFEST.txt"
    lines = sorted(written)
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {
        "duckdb": str(db_path),
        "output_dir": str(dest),
        "manifest": str(manifest),
        "n_files": str(len(lines) + 1),
    }


def _package_readme() -> str:
    return f"""# bets-cerveja — dataset derivado

Pacote para o Zenodo. Só dado **derivado**: Parquet dos marts,
PNG das figuras e atribuição. Não inclui DuckDB, `.env`, lake DVC
nem bytes de `data/00_landing`.

DOI (placeholder até reservar o recorde): {DOI_PLACEHOLDER}

Código: {REPO_URL} (MIT). Dados derivados: [LICENSE-DATA](LICENSE-DATA)
(CC BY 4.0).

## O que é cada arquivo

- `marts/agg_panorama_mensal.parquet` — Ato 1, SIDRA 8885 11.1
  (PIM geral / IPCA só como contexto)
- `marts/fct_mercado_cerveja_anual.parquet` — produção anual MAPA
  (2024 em dois vintages, sem média)
- `marts/fct_cerveja_previsao.parquet` — contrafactual SARIMAX
  (realizado, previsto, IC 95%)
- `marts/agg_de_onde_saiu_o_dinheiro.parquet` — Ato 2, Locomotiva p. 19
- `marts/agg_estrutura_setorial.parquet` — Ato 3, IEPS vs IBJR (sem média)
- `marts/qa_divergencias.parquet` — divergências rotuladas
- `marts/agg_indicadores_declarados.parquet` — proveniência / citações
- `marts/ml_metricas.parquet` — uma linha por execução SARIMAX
- `marts/ml_coeficientes.parquet` — coeficientes, erro padrão, p-valor, IC
- `figures/*.png` + `figures/index.html` — os cinco gráficos e o índice
- `LICENSE-DATA` — CC BY 4.0 dos derivados
- `CITATION.cff` / `.zenodo.json` — metadados (DOI placeholder)
- `MANIFEST.txt` — lista dos arquivos deste pacote

## Como ler a ponte Locomotiva

48% dos apostadores das classes C/D/E dizem ter tirado dinheiro de
bares, restaurantes e delivery. Isso é **survey**, não substituição
litro a litro de cerveja. Nenhuma fonte do acervo liga, de forma
quantificada, redução de consumo de cerveja a aumento de gasto com
apostas.

Mix de produto (cerveja sem álcool 4,9%→1,27% e o V de puro malte)
**não entra no gráfico**. Ver `qa_divergencias` e a documentação do
repositório.

## Atribuição das fontes primárias

- MAPA — Anuário da Cerveja (produção anual, emprego na fabricação)
- IBGE — SIDRA 8885 (PIM bebidas), 8888 (PIM geral), 7060 (IPCA cerveja)
- BCB — SGS 24364 (rendimento real); Estudo Especial 119 (fluxo Pix)
- Instituto Locomotiva / Strategy& — survey de substituição (p. 19)
- IEPS — empregos formais no setor de apostas
- IBJR / ANJL / LCA — panorama de apostas (diretos e indiretos;
  conflito de interesse)
- Demais citações em `agg_indicadores_declarados` e `qa_divergencias`

Os bytes originais (PDF/HTML/JSON de `data/00_landing`) continuam sob
a licença de cada publicador. Este pacote não os republica.

## O que isto não é

Não é GGR da SPA. Não é evidência causal de que as bets “pegaram”
litros de cerveja. O contrafactual SARIMAX descreve ausência de
anomalia agregada na série SIDRA 8885 11.1.
"""

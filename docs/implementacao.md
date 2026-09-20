# Implementação

Checklist operacional. Etapas: [etapas.md](etapas.md). Arquitetura: [architecture.md](architecture.md). Grain: [grain.md](grain.md). Matriz: [fontes_lacunas.md](fontes_lacunas.md).

## O que está no repositório

- Fundação Python 3.12, CLI de fontes, lake em `00_landing`, DVC no R2.
- Panorama IBJR/ANJL no lake (tier C). SPA **fora de escopo** ([ADR 0004](adr/0004-sem-panorama-spa.md)).
- Make: `test`, `lint`, `sources`, `ingest`, `extract`, `dbt-build`, `sarimax`, `figures`, `demo`, `dvc-push`, `dvc-pull`, `ci`, `dagster-dev`.
- Extract de API (SIDRA/BCB) → `data/01_raw/.../extract.parquet` (`RawApiSeries`).
- Classificação do mix (SIDRA 8885 e Anuário) em [fontes_lacunas.md](fontes_lacunas.md):
  1. Cerveja sem álcool na SIDRA 8885 fica em **11.1** (`129192`), não em 11.2.
  2. Queda 4,9% → 1,27% do mix sem álcool é **quebra metodológica** (numerador muda; o denominador da retificação de 2024 não explica).
  3. Puro malte 29,2% → 24,7% → 29,2% são **três medidas de vintage**; o 24,7% não some na revisão de 2024.
- dbt-duckdb materializa `marts_core` em `warehouse/betscerveja.duckdb`.
- Testes `relationships` (e FK composta para `dim_fonte`), `qa_divergencias` e `marts_analytics` (`agg_*`).
- Dagster (`make dagster-dev`), GitHub Actions (lint → test → dvc pull → dbt build) e Pages com o catálogo `dbt docs`.
- SARIMAX / `marts_ml` (`ml_dataset_cerveja_mensal` no dbt; `fct_cerveja_previsao`, `ml_metricas`, `ml_coeficientes` no Python).
- Figuras matplotlib em `exports/figures/` (`make figures`). [ADR 0005](adr/0005-figuras-em-vez-de-power-bi.md).
- `make demo` (sample commitado → dbt → SARIMAX → figuras → `exports/zenodo/`). DOI reservado: [10.5281/zenodo.22863812](https://doi.org/10.5281/zenodo.22863812).

## Ações externas (não são código)

R2 já está. No GitHub: criar os secrets `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY` (o mesmo par do `.env` local / R2) e em Settings → Pages → Source = GitHub Actions.

Zenodo (não há token no repositório):

DOI reservado: [10.5281/zenodo.22863812](https://doi.org/10.5281/zenodo.22863812). `CITATION.cff` e `.zenodo.json` já apontam para ele.

1. No rascunho do recorde: substituir os arquivos pelo `exports/zenodo/` regenerado (para o README do pacote não sair com placeholder).
2. Conferir que o DOI reservado bate com o dos arquivos.
3. **Publish**. Depois disso o DOI é permanente.

## Comandos

```powershell
uv sync --extra dev
make sources
make test
make dvc-pull
uv run betscerveja ingest --source sidra_8885_pim_bebidas
uv run betscerveja extract --source sidra_8885_pim_bebidas
uv run betscerveja extract --source sidra_8888_pim_geral
uv run betscerveja extract --source sidra_7060_ipca
uv run betscerveja extract --source bcb_sgs_rendimento_real
uv run betscerveja extract --source anuario_cerveja_ref2025_pub2026
make extract
make dbt-build
make sarimax
make figures
make demo
make ci
make dagster-dev
```

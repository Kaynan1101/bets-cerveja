# Implementação — o que está feito e o que você precisa fazer

Checklist operacional. Etapas numeradas: [etapas.md](etapas.md). Arquitetura: [architecture.md](architecture.md). Grain: [grain.md](grain.md). Matriz: [fontes_lacunas.md](fontes_lacunas.md).

## Feito

- Fundação Python 3.12, CLI de fontes, lake em `00_landing`, DVC no R2.
- Panorama IBJR/ANJL no lake (tier C). SPA **fora de escopo** (ADR 0004).
- Make: `test`, `lint`, `sources`, `ingest`, `extract`, `dbt-build`, `sarimax`, `dvc-push`, `dvc-pull`, `ci`, `dagster-dev`.
- Extract de API (SIDRA/BCB) → `data/01_raw/.../extract.parquet` (`RawApiSeries`).
- Etapa 4: três perguntas de classificação respondidas em [fontes_lacunas.md](fontes_lacunas.md). Briefing: [etapa_4.md](etapa_4.md).
  1. Cerveja sem álcool na SIDRA 8885 fica em **11.1** (`129192`), não em 11.2.
  2. Queda 4,9% → 1,27% do mix sem álcool é **quebra metodológica** (numerador muda; o denominador da retificação de 2024 não explica).
  3. Puro malte 29,2% → 24,7% → 29,2% são **três medidas de vintage**; o 24,7% não some na revisão de 2024.
- Etapa 5: dbt-duckdb materializa `marts_core` em `warehouse/betscerveja.duckdb`. Briefing: [etapa_5.md](etapa_5.md).
- Etapa 6: testes `relationships` (e FK composta para `dim_fonte`), `qa_divergencias` e `marts_analytics` (`agg_*`). Briefing: [etapa_6.md](etapa_6.md).
- Etapa 7: Dagster (`make dagster-dev`), GitHub Actions (lint → test → dvc pull → dbt build) e Pages com o catálogo `dbt docs`. Briefing: [etapa_7.md](etapa_7.md).
- Etapa 8: SARIMAX / `marts_ml` (`ml_dataset_cerveja_mensal` no dbt; `fct_cerveja_previsao`, `ml_metricas`, `ml_coeficientes` no Python). Briefing: [etapa_8.md](etapa_8.md).

## Ainda não

- Etapa 9: figuras matplotlib em `exports/figures/` — não Power BI. `make figures` ainda não existe. [ADR 0005](adr/0005-figuras-em-vez-de-power-bi.md), briefing: [etapa_9.md](etapa_9.md).
- Etapa 10: `make demo` e Zenodo.

## Ações suas (externas)

R2 já está. No GitHub: criar os secrets `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY` (o mesmo par do `.env` local / R2) e em Settings → Pages → Source = GitHub Actions. Zenodo só na etapa 10, se você quiser DOI.

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
make ci
make dagster-dev
```

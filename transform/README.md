# transform (dbt + DuckDB)

dbt entra na **etapa 5**. Star schema em `marts_core`; qualidade e agregados em `marts_analytics` (etapa 6). Sem `dbt_utils`: `dim_data` é spine SQL no DuckDB. FKs nativas (`relationships`) e a FK composta `(source_id, vintage_publicacao)` → `dim_fonte` rodam no `dbt build`.

## Como rodar

Na raiz do repositório, com o lake em `data/01_raw` (se estiver vazio: `make dvc-pull`; APIs: `make extract`):

```powershell
uv sync --extra dev
make dbt-build
```

Equivalente: `uv run python scripts/export_dbt_seeds.py` e `uv run dbt build --project-dir transform --profiles-dir transform`.

O warehouse fica em `warehouse/betscerveja.duckdb` (gitignored).

## Camadas

| Pasta | Schema DuckDB | Papel |
| --- | --- | --- |
| `models/staging/` | `main_staging` | 1:1 com Parquet (`RawApiSeries` / `RawExtract`) |
| `models/intermediate/` | `main_intermediate` | Período, filtro 8885 11.1, item IPCA cerveja, parse do Anuário |
| `models/marts/core/` | `main_marts_core` | Dimensões e fatos de [`docs/grain.md`](../docs/grain.md) |
| `models/marts/analytics/` | `main_marts_analytics` | `agg_*` e `qa_divergencias` (Ato 1–3). Folha do DAG. |
| `models/marts/ml/` | `main_marts_ml` | `ml_dataset_cerveja_mensal` (dbt). Forecast SARIMAX é Python. |

`marts_ml` na etapa 8: o dataset `ml_dataset_cerveja_mensal` é dbt (`models/marts/ml/`). As três saídas do Python (`fct_cerveja_previsao`, `ml_metricas`, `ml_coeficientes`) **não** são models dbt — o forecast não cabe em SQL. No DuckDB o schema aparece como `main_marts_ml` (prefixo do profile), o mesmo padrão de `main_marts_core`.

Seeds `seed_metricas` e `seed_fontes` são gerados de `conf/metrics.yml` e `conf/sources.yml`. `seed_citacoes` é só indicador esparso citável (e fallback da produção MAPA).

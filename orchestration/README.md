# Orquestração (etapa 7)

Dagster materializa cada model dbt como asset (`dagster-dbt`). Ingest e extract das fontes que o warehouse lê são jobs à parte; a CI não os dispara.

Suba a UI local:

```powershell
make dagster-dev
```

Equivalente: `uv run dagster dev -m orchestration.definitions`.

Na UI, o job `build_warehouse` só corre `dbt build`. Rede (SIDRA/BCB/PDF) fica em `ingest_sources` e `extract_sources`. O job `build_forecast` chama o SARIMAX (mesma função de `betscerveja forecast`) e não dispara ingest; o dataset `ml_dataset_cerveja_mensal` precisa já estar materializado.

Ver [ADR 0001](../docs/adr/0001-orquestracao-dagster-em-vez-de-airflow.md).

# ADR 0001 — Orquestração com Dagster, não Airflow

- Status: aceito
- Data: 2026-09-15

## Contexto

O pipeline é mensal, cabe em dezenas de megabytes e precisa de linhagem visível do PDF do Anuário até o mart. A Fase 5 pede um orquestrador de verdade, depois de CLI + Makefile.

## Decisão

Usar Dagster com `dagster-dbt` a partir da Fase 5. Não instalar Airflow neste repositório.

## Consequências

- `dbt build` deixa de ser um retângulo opaco: cada model vira asset.
- Roda nativo no Windows do desenvolvimento.
- Menos conhecido em vagas "de mercado" que pedem Airflow pelo nome.

## Alternativas rejeitadas

- **Airflow** (CeleryExecutor + Postgres + Redis): sete containers para um pipeline solo. Não é nativo no Windows. Linhagem dbt some dentro de um operador.
- **Ficar só no Makefile:** suficiente até a Fase 4. Não escala para partições mensais e sensores de API.

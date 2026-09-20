# Etapas do pipeline

Ordem em que o repositório foi construído. Grain no dbt veio antes de figuras e SARIMAX.

| Etapa | O quê | Pronto quando |
| --- | --- | --- |
| 0 | Fundação, lake, DVC R2 | commit `0972bd2` |
| 1 | SPA fora de escopo; grain sem `fct_apostas_oficial` | `sources validate` lista 1 fora de escopo |
| 2 | Ingest SIDRA/BCB + `_manifest.jsonl` | `betscerveja ingest --source sidra_8885_pim_bebidas` idempotente |
| 3 | Extrair PDFs/HTML do lake → `01_raw` Parquet + DVC | `dvc add data/01_raw` e `make dvc-push` |
| 4 | Ler metadados SIDRA 8885 e as tabelas de mix do Anuário | três perguntas de classificação em [fontes_lacunas.md](fontes_lacunas.md) |
| 5 | dbt + DuckDB (staging → marts) | `dbt build` no star schema |
| 6 | Qualidade e `qa_divergencias` | testes unique/relationships verdes |
| 7 | Dagster + GitHub Actions + Pages | CI roda lint, dvc pull, dbt build |
| 8 | SARIMAX contrafactual | `fct_cerveja_previsao` materializado |
| 9 | Figuras estáticas (três atos + contrafactual + proveniência) | `make figures` gera PNG + HTML em `exports/figures/` |
| 10 | Demo e pacote Zenodo | `make demo` |

As dez etapas estão fechadas. Como rodar: [implementacao.md](implementacao.md).

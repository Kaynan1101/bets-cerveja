# Etapas até o fim

Ordem fixa. Não pular para Power BI ou SARIMAX antes do grain estar no dbt. Tarefas no Cursor acompanham esta lista.

| Etapa | O quê | Pronto quando |
| --- | --- | --- |
| 0 | Fundação, lake, DVC R2 | commit `0972bd2` |
| 1 | SPA fora de escopo; grain sem `fct_apostas_oficial` | `sources validate` lista 1 fora de escopo |
| 2 | Ingest SIDRA/BCB + `_manifest.jsonl` | `betscerveja ingest --source sidra_8885_pim_bebidas` idempotente |
| 3 | Extrair PDFs/HTML do lake → `01_raw` Parquet + DVC | `dvc add data/01_raw` e `make dvc-push` |
| 4 | Ler metadados SIDRA 8885 e as tabelas de mix do Anuário | três perguntas de classificação respondidas em `docs/fontes_lacunas.md` |
| 5 | dbt + DuckDB (staging → marts) | `dbt build` no star schema |
| 6 | Qualidade e `qa_divergencias` | testes unique/relationships verdes |
| 7 | Dagster + GitHub Actions + Pages | CI roda lint, dvc pull, dbt build |
| 8 | SARIMAX contrafactual | `fct_cerveja_previsao` materializado |
| 9 | Power BI (cinco páginas) | `.pbix` + PNG |
| 10 | Demo, Zenodo (conta sua) | `make demo` |

Etapa atual: **5** (dbt). Etapas **1–4** feitas. Briefing da etapa 4 (histórico): [etapa_4.md](etapa_4.md).

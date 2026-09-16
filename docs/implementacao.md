# Implementação — o que está feito e o que você precisa fazer

Este arquivo é o checklist operacional. A arquitetura está em [architecture.md](architecture.md). A chave das tabelas está em [grain.md](grain.md). A matriz afirmação → fonte está em [fontes_lacunas.md](fontes_lacunas.md).

## Feito nesta fundação (Fase 0, parcial)

- `.gitignore` protege o lake. `git add .` **não** deve commitar PDFs.
- Python 3.12 via `uv` (`requires-python = ">=3.12,<3.13"`). O Python 3.14 da máquina não é usado.
- CLI `betscerveja sources list|show|validate` lendo `conf/sources.yml` com Pydantic.
- Acervo em `data/00_landing/<id>/seed/`, Anuários com `ref` e `pub` no nome, pastas `*_files` descartadas.
- Panorama LCA+Cruz / IBJR / ANJL (nov/2025) registrado como fonte **tier C**. Não é o Panorama da SPA.
- GNU Make: `make test`, `make lint`, `make sources`, `make dvc-push`, `make dvc-pull`.
- DVC no Cloudflare R2: `data/00_landing` versionado (25 arquivos, ~55 MB). Credenciais só em `.env` e `.dvc/config.local`.
- Documentação de implementação, grain, lacunas e ADRs.

## O que ainda não é código (e não deve ser)

A Fase 1 (ingest) e a Fase 2 (extract) só começam depois das três verificações bloqueantes.

## Ações suas (externas)

### Cloudflare R2 — feito

Remote `r2` aponta para `s3://bets-cerveja-landing`. `dvc push` já subiu o landing. Secrets ficam em `.dvc/config.local` (gitignore). boto3 novo precisa das flags de checksum no `.env` (veja `.env.example`); sem elas o R2 responde AccessDenied no PutObject.

`data/01_raw` ainda não está no DVC: só tem README no Git. Entra no DVC quando a extração gerar Parquet.

```powershell
make dvc-push
make dvc-pull
```

GitHub Secrets para o Actions só na Fase 5.

### Panorama da SPA / Ministério da Fazenda

Fonte oficial de GGR e apostadores. **Continua ausente.** O PDF da IBJR/ANJL não substitui. Página: https://www.gov.br/fazenda/pt-br/composicao/orgaos/secretaria-de-premios-e-apostas

## Verificações bloqueantes (antes da Fase 2)

Não modelar até responder:

1. Onde o IBGE classifica cerveja sem álcool na SIDRA 8885 — 11.1 (alcoólicas) ou 11.2 (não alcoólicas)?
2. Por que sem álcool cai de 4,9% (2024) para 1,27% (2025) no Anuário, se o Euromonitor segue em alta?
3. Por que puro malte faz 29,2% → 24,7% → 29,2% entre 2023 e 2025?

A (1) decide se o SARIMAX mede hábito ou reclassificação de gaveta. As outras duas decidem se a composição do Anuário é comparável entre vintages.

## Fases seguintes (não executar agora)

| Fase | Entrega | Comando-alvo |
| --- | --- | --- |
| 1 | Adapters SIDRA/BCB/HTTP + `_manifest.jsonl` + idempotência por sha256 | `uv run betscerveja ingest --source sidra_8885_pim_bebidas` |
| 2 | Extração Parquet + pandera; revisão humana no Panorama SPA | `uv run betscerveja extract --source <id>` |
| 3 | DuckDB + dbt staging → intermediate → marts_core/analytics | `uv run dbt build --project-dir transform` |
| 4 | Testes de qualidade e `qa_divergencias` | `dbt test` |
| 5 | Dagster + GitHub Actions + `dbt docs` no Pages | precisa de remote DVC e Pages |
| 6 | SARIMAX (treino até 2022, projeção 2023–2026) | `uv run betscerveja forecast` |
| 7 | `exports/powerbi/` + `.pbix` | Power BI Desktop (licença Pro se quiser link público) |
| 8 | demo, DOI Zenodo | Zenodo é conta externa |

## Comandos desta fase

```powershell
uv sync --extra dev
make sources
make test
make lint
uv run betscerveja sources show lca_ibjr_anjl_panorama_apostas_2025
```

`make` é atalho para os `uv run` acima e o mesmo alvo que o CI Linux vai usar depois. Não substitui a CLI.

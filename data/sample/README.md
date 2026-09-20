# Amostra commitada para `make demo`

Fatia **commitada no Git** para rodar o demo **sem Cloudflare R2**. São os sete `extract.parquet` que o dbt lê, na **mesma árvore** de `data/01_raw/`. Dados derivados ([LICENSE-DATA](../../LICENSE-DATA), CC BY 4.0) — **não** bytes de `data/00_landing`.

A CI **não** usa esta pasta. O job continua `dvc pull` + `data/01_raw`. Sample não mascara falha de DVC.

A série SIDRA/BCB aqui é a série **cheia** (o treino SARIMAX precisa de meses pré-2023). “Fatia pequena” = Parquet extraído em vez de PDF/HTML do lake, não um recorte 2023–2026.

## Como atualizar

Depois de `make dvc-pull` e extract no lake:

```powershell
uv run python scripts/sync_sample.py
```

Se `data/01_raw` estiver vazio, o script **para**. Não invente Parquet sintético.

# Registro de fontes

A fonte da verdade é [`conf/sources.yml`](../conf/sources.yml), validada por [`src/betscerveja/registry.py`](../src/betscerveja/registry.py).

```powershell
uv run betscerveja sources list
uv run betscerveja sources show anuario_cerveja_ref2025_pub2026
uv run betscerveja sources validate
```

## Campos que não podem faltar

| Campo | Por quê |
| --- | --- |
| `ano_referencia` vs `vintage_publicacao` | Sem os dois, a revisão de 2024 vira um único número errado |
| `tier_confiabilidade` A/B/C | Survey e Klavi não pesam igual ao MAPA |
| `e_oficial` | Destaca SIDRA/MAPA/BCB |
| `conflito_de_interesse` | CISA é financiado por AmBev e Heineken; IBJR/ANJL representam operadoras |
| `status_acervo` | `no_lake` / `pendente` / `planejada` / `fora_de_escopo` |
| `landing_filename` | Nome canônico no lake, sem mojibake |
| `api_path` | Caminho da API SIDRA/SGS na ingestão |

## Como o Anuário foi renomeado

O arquivo original `anuario-da-cerveja-2025.pdf` é o Anuário **2026**, dados de **2025**. No lake:

`anuario_cerveja_ref2025_pub2026.pdf`

## Fora de escopo

- `spa_panorama_apostas_2025` — ADR 0004. GGR oficial não entra.

## APIs no lake (SIDRA e BCB)

Ingest via `betscerveja ingest`; série tidy via `betscerveja extract` (schema `RawApiSeries`).

| id | Adapter | O que entra no Parquet |
| --- | --- | --- |
| `sidra_8885_pim_bebidas` | `api_sidra` | Índice PIM-PF, classificação 542, categorias 11.1 (`129192`) e 11.2 (`129193`) |
| `sidra_8888_pim_geral` | `api_sidra` | PIM-PF geral, classificação 544 categoria **1 Indústria geral** (`129314`) |
| `sidra_7060_ipca` | `api_sidra` | IPCA variável 63; filtrar item cerveja (classificação 315) no dbt |
| `bcb_sgs_rendimento_real` | `api_bcb` | SGS 24364; `periodo` = data do ponto; classificação nula |

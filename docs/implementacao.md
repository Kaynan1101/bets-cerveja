# Implementação — o que está feito e o que você precisa fazer

Checklist operacional. Etapas numeradas: [etapas.md](etapas.md). Arquitetura: [architecture.md](architecture.md). Grain: [grain.md](grain.md). Matriz: [fontes_lacunas.md](fontes_lacunas.md).

## Feito

- Fundação Python 3.12, CLI de fontes, lake em `00_landing`, DVC no R2.
- Panorama IBJR/ANJL no lake (tier C). SPA **fora de escopo** (ADR 0004).
- Make: `test`, `lint`, `sources`, `ingest`, `extract`, `dvc-push`, `dvc-pull`.
- Extract de API (SIDRA/BCB) → `data/01_raw/.../extract.parquet` (`RawApiSeries`).
- Etapa 4: três perguntas de classificação respondidas em [fontes_lacunas.md](fontes_lacunas.md). Briefing: [etapa_4.md](etapa_4.md).
  1. Cerveja sem álcool na SIDRA 8885 fica em **11.1** (`129192`), não em 11.2.
  2. Queda 4,9% → 1,27% do mix sem álcool é **quebra metodológica** (numerador muda; o denominador da retificação de 2024 não explica).
  3. Puro malte 29,2% → 24,7% → 29,2% são **três medidas de vintage**; o 24,7% não some na revisão de 2024.

## Ações suas (externas)

R2 já está. GitHub Secrets só na etapa 7. Zenodo só na etapa 10, se você quiser DOI.

## Comandos

```powershell
uv sync --extra dev
make sources
make test
uv run betscerveja ingest --source sidra_8885_pim_bebidas
uv run betscerveja extract --source sidra_8885_pim_bebidas
uv run betscerveja extract --source sidra_8888_pim_geral
uv run betscerveja extract --source sidra_7060_ipca
uv run betscerveja extract --source bcb_sgs_rendimento_real
uv run betscerveja extract --source anuario_cerveja_ref2025_pub2026
make extract
```

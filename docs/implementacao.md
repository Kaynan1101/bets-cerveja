# Implementação — o que está feito e o que você precisa fazer

Checklist operacional. Etapas numeradas: [etapas.md](etapas.md). Arquitetura: [architecture.md](architecture.md). Grain: [grain.md](grain.md). Matriz: [fontes_lacunas.md](fontes_lacunas.md).

## Feito

- Fundação Python 3.12, CLI de fontes, lake em `00_landing`, DVC no R2.
- Panorama IBJR/ANJL no lake (tier C). SPA **fora de escopo** (ADR 0004).
- Make: `test`, `lint`, `sources`, `dvc-push`, `dvc-pull`.

## Ações suas (externas)

R2 já está. GitHub Secrets só na etapa 7. Zenodo só na etapa 10, se você quiser DOI.

Briefing completo da etapa 4 (para um agente novo executar): [etapa_4.md](etapa_4.md).

## Verificações (antes de modelar no dbt — etapa 4)

Não bloqueiam baixar a SIDRA nem extrair o Anuário:

1. Onde o IBGE classifica cerveja sem álcool na SIDRA 8885 — 11.1 ou 11.2?
2. Por que sem álcool cai de 4,9% (2024) para 1,27% (2025) no Anuário?
3. Por que puro malte faz 29,2% → 24,7% → 29,2%?

## Comandos

```powershell
uv sync --extra dev
make sources
make test
uv run betscerveja ingest --source sidra_8885_pim_bebidas
uv run betscerveja extract --source anuario_cerveja_ref2025_pub2026
```

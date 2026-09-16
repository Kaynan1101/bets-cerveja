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
| `e_oficial` | Destaca SIDRA/MAPA/BCB/SPA |
| `conflito_de_interesse` | CISA é financiado por AmBev e Heineken; Klavi vende Open Finance |
| `status_acervo` | `no_lake` / `pendente` / `planejada` |
| `landing_filename` | Nome canônico no lake, sem mojibake |

## Como o Anuário foi renomeado

O arquivo original `anuario-da-cerveja-2025.pdf` é o Anuário **2026**, dados de **2025**. No lake:

`anuario_cerveja_ref2025_pub2026.pdf`

## Pendências de coleta

- `spa_panorama_apostas_2025` — oficial (GGR, apostadores, destinações). **Ainda não está no acervo.** O PDF `LCA_Cruz_IBJR_ANJL_Panorama-2025-Setor.pdf` é o panorama LCA+Cruz/IBJR/ANJL (`lca_ibjr_anjl_panorama_apostas_2025`), não substitui a SPA.
- APIs SIDRA 8885/8888/7060 e BCB SGS — Fase 1, sem conta (endpoints públicos).

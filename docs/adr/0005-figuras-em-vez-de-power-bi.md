# ADR 0005 — Figuras matplotlib em vez de Power BI

- Status: aceito
- Data: 2026-09-20
- Supersede: a etapa 9 de [etapas.md](../etapas.md) deixou de ser “cinco páginas `.pbix`”

## Contexto

O plano original pedia Power BI Desktop, `make export` para Parquet e cinco páginas. O que o warehouse realmente entrega para mostrar:

- Ato 1: série mensal SIDRA 8885 (um recorte Brasil) + 3–4 pontos anuais MAPA, com 2024 em dois vintages
- Ato 2: survey Locomotiva de um corte; EE119 de um mês
- Ato 3: duas linhas de emprego (IEPS vs IBJR), definições distintas
- Proveniência: tabela de citação
- Contrafactual: uma banda SARIMAX

Mix sem álcool e V de puro malte já estão fora do gráfico ([fontes_lacunas.md](../fontes_lacunas.md)). Não há drill-down, não há modelo compartilhado, e o GitHub Pages já publica o catálogo dbt.

## Decisão

Etapa 9 é `make figures`: matplotlib lê o DuckDB e grava PNG + um HTML curto em `exports/figures/`. Sem `.pbix`, sem Power BI Desktop, sem `exports/powerbi/`.

O HTML das figuras entra no `make demo` da etapa 10. Pages continua sendo só o catálogo dbt.

## Consequências

- Star schema e `marts_analytics` alimentam figuras, não um modelo semântico.
- Poucos pontos ficam explícitos (dois 2024, duas definições de emprego). Um dashboard esconderia isso atrás de slicer.
- PNG versionado no git; HTML sem JavaScript de charting.
- CI não publica as figuras (demo é etapa 10).

## Alternativas rejeitadas

**Power BI (cinco páginas).** Overhead de Desktop, arquivo binário e `make export` para um deck narrativo de ~4 figuras e 2 tabelas.

**Streamlit / Dash.** App interativo para dado que não se fatia. Mais runtime que o demo precisa.

**Plotly / Vega.** Hover é útil, mas acrescenta JS e dependência. matplotlib cobre PNG reproduzível para artigo e demo.

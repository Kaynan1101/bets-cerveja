# Figuras estáticas (etapa 9)

PNG + HTML gerados por `make figures` a partir do DuckDB. Briefing: [`docs/etapa_9.md`](../../docs/etapa_9.md). Decisão: [ADR 0005](../../docs/adr/0005-figuras-em-vez-de-power-bi.md).

## Como gerar

Requer warehouse + forecast já materializados (`make dbt-build` e `make sarimax`). Depois:

```powershell
make figures
```

Equivalente: `uv run betscerveja figures`. Saída default: este diretório. Override do DuckDB: `BETSCERVEJA_DUCKDB_PATH`.

`make figures` **não** entra em `make ci`. `make demo` (etapa 10) regenera estas figuras a partir de `data/sample/` e copia PNG + HTML para `exports/zenodo/`. Pages continua sendo só o catálogo dbt.

## Artefatos

- `ato1_panorama.png` — `agg_panorama_mensal` (SIDRA 8885 11.1; PIM geral / IPCA só como contexto)
- `ato1_producao_anual.png` — `fct_mercado_cerveja_anual` (dois vintages de 2024 visíveis)
- `ato1_sarimax.png` — `fct_cerveja_previsao` (realizado, previsto, IC 95%)
- `ato2_substituicao.png` — `agg_de_onde_saiu_o_dinheiro` (Locomotiva p. 19)
- `ato3_emprego.png` — `agg_estrutura_setorial` / `qa_divergencias` (IEPS vs IBJR, sem média)
- `index.html` — os PNG + proveniência (`agg_indicadores_declarados`) + `qa_divergencias`

Não plotar `agg_mix_produto`. Sem sparkline 4,9%→1,27% nem V de puro malte. Sem Power BI, sem `.pbix`, sem Plotly/Vega/Streamlit.

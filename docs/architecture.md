# Arquitetura

Janela 2023–2026. Eixo: substituição de orçamento. Camadas Medallion com fronteira rígida entre I/O e SQL de negócio.

```mermaid
flowchart TB
    subgraph src [Fontes]
        A1[APIs SIDRA e BCB]
        A2[PDFs oficiais e pesquisa]
        A3[HTML jornalístico]
    end
    subgraph ing [Ingestao]
        B1[Typer adapters]
    end
    C1[00_landing bytes + sha256]
    subgraph extract [Extracao]
        D1[pdfplumber camelot trafilatura]
    end
    E1[01_raw Parquet]
    subgraph wh [DuckDB dbt]
        F2[staging]
        F3[intermediate]
        F4[marts_core]
        F5[marts_analytics]
        F6[marts_ml]
    end
    H1[SARIMAX]
    G1[figuras matplotlib]
    A1 --> B1 --> C1 --> D1 --> E1 --> F2 --> F3 --> F4 --> F5
    F4 --> H1 --> F6
    F4 --> G1
    F5 --> G1
    F6 --> G1
```

## Por que cada ferramenta está onde está

| Camada | Ferramenta | Motivo |
| --- | --- | --- |
| Fundação | `uv` + Python 3.12 | Lockfile. 3.14 da máquina não tem wheel estável para dbt/camelot. |
| Ingestão | Typer, httpx, tenacity | I/O sujo. dbt não faz chamada de rede: se a SIDRA cair, `dbt build` ainda roda no raw. |
| Extração | pdfplumber / camelot / trafilatura / pandera | Parser evolui sem rebaixar. pandera testa forma; dbt testa semântica. |
| Lake | Parquet + DVC (Cloudflare R2) | Landing imutável. Drive exigiria service account no CI. |
| Warehouse | DuckDB | Um arquivo, zero servidor. `*.duckdb` no `.gitignore`. |
| Transformação | dbt-duckdb | Todo SQL de negócio. Lineage e testes colados no model. |
| Orquestração | Dagster na etapa 7 | Ver [ADR 0001](adr/0001-orquestracao-dagster-em-vez-de-airflow.md). |
| ML | statsmodels SARIMAX na etapa 8 | Coeficiente, IC e p-valor. Precisamos poder dizer "efeito indistinguível de zero". |
| Apresentação | matplotlib na etapa 9 | Consome o DuckDB; grava `exports/figures/*.png` + HTML. Poucos pontos; sem modelo semântico. Ver [ADR 0005](adr/0005-figuras-em-vez-de-power-bi.md). |

## Três schemas de marts

- `marts_core` — star schema estável. Entra nas figuras (produção anual, etc.).
- `marts_analytics` — agregados por pergunta (Ato 1, 2 e 3). Folha do DAG, reescrevível.
- `marts_ml` — saída do contrafactual, lida pelas figuras na banda de confiança.

## Narrativa que a arquitetura precisa sustentar

1. **Ato 1.** A cerveja não caiu no agregado, e a manchete de 2025 inverte conforme o vintage de 2024. Fecha com o contrafactual dentro do intervalo.
2. **Ato 2.** De onde saiu o dinheiro (Locomotiva / Fundaj / BCB / Klavi) e o que mudou por dentro do mix de cerveja.
3. **Ato 3.** Contraste estrutural (emprego, receita, custo social) e hipóteses rivais, com os limites ditos em voz alta.

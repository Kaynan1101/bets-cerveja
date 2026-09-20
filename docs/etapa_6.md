# Briefing para o agente — etapa 6

**Status: feita** (critério de pronto fechado). Não avançar daqui para Dagster, SARIMAX, Power BI ou Zenodo.

Cole o bloco abaixo num chat novo (Agent mode) e anexe este arquivo se quiser. O agente deve **executar** o briefing, não reescrever o plano.

```
Implemente a etapa 6 deste repositório. Siga docs/etapa_6.md até o critério de pronto.
Não avance para etapa 7 (Dagster / GitHub Actions / Pages), SARIMAX, Power BI ou Zenodo.
Não altere docs/grain.md.
```

---

## Contexto do projeto

`bets-cerveja` é um **pipeline de pesquisa**, não um app de apostas. Pergunta: de onde saiu o dinheiro das bets no Brasil (2023–2026), em especial o canal on-premise (bares/restaurantes/delivery). Cerveja agregada não caiu; a ponte empírica é o survey Locomotiva (48% C/D/E dizem ter tirado dinheiro de bares/restaurantes/delivery).

Ordem fixa em [`docs/etapas.md`](etapas.md). Etapas **1–5 feitas**. Esta tarefa é **só a etapa 6** (qualidade, `qa_divergencias`, `marts_analytics`). Grain em [`docs/grain.md`](grain.md) — **não alterar**. Arquitetura: [`docs/architecture.md`](architecture.md). Matriz de afirmações e divergências: [`docs/fontes_lacunas.md`](fontes_lacunas.md). Métricas: [`docs/data_dictionary.md`](data_dictionary.md) e [`conf/metrics.yml`](../conf/metrics.yml). Briefing da etapa 5 (já executado): [`docs/etapa_5.md`](etapa_5.md).

Stack: Python 3.12 (`requires-python = ">=3.12,<3.13"`), `uv`, Typer, Parquet, DVC → R2, pandera, **dbt-duckdb**. Warehouse em `warehouse/betscerveja.duckdb` (gitignored).

Numeração antiga vs canônica: docs antigos dizem “Fase 3 = dbt” e “Fase 5 = Dagster”. Ignorar. **Dagster é etapa 7.** Não instalar Dagster nesta etapa.

## Estado atual do código

| Camada | Status |
| --- | --- |
| Lake DVC (`00_landing`, `01_raw`) | pronto |
| Extract API + PDF/HTML | pronto |
| `transform/` dbt-duckdb | **pronto (etapa 5)** — staging → intermediate → `marts_core` |
| Testes `unique` / `unique_combination` nas chaves de grain | prontos, contrato enforced |
| Testes `relationships` | **falta** |
| `qa_divergencias` | **falta** |
| `marts_analytics` (`agg_*`) | **falta** |
| Makefile | `dbt-build` já existe |
| Dagster, SARIMAX, Power BI | fora de escopo desta etapa |

Seeds: `seed_metricas`, `seed_fontes` gerados por [`scripts/export_dbt_seeds.py`](../scripts/export_dbt_seeds.py); `seed_citacoes` tem Locomotiva p. 19, EE119, Klavi, IEPS, IBJR e fallback da produção MAPA.

`dim_fonte.fonte_id` = `source_id || '|' || vintage_publicacao`. APIs usam `vintage_publicacao = 0`. Fatos guardam `source_id` + `vintage_publicacao`, não `fonte_id`. `dim_data` cobre 2002-01-01 a 2026-12-31.

`stg_raw_pdf` une só os Anuários 2023–2025. Anuários 2021–2022 estão no lake só como contexto / QA (ADR 0002).

`spa_panorama_apostas_2025` está `fora_de_escopo`. **Não** criar `fct_apostas_oficial`. **Não** materializar `ggr` nem `destinacoes_legais` como linhas de fato.

## Critério de pronto

`dbt build` materializa `marts_core` + `marts_analytics` (incluindo `qa_divergencias`). Testes `unique` e `relationships` passam. `make test` e `make lint` continuam verdes.

Pronto quando:

1. `make dbt-build` roda sem erro
2. Todo fato/dim de `marts_core` tem `relationships` (ou FK composta) para as dims usadas
3. Existe `qa_divergencias` com grain métrica × período × par de fontes/vintages
4. `qa_divergencias` contém o par 15,344 vs 17,211 bi L de 2024 e o par IEPS vs IBJR de emprego
5. Existem os `agg_*` listados em grain.md sob Analytics (ver Tarefa 3)
6. `ggr` / `destinacoes_legais` **não** aparecem como linhas de fato nem de agg
7. Mix sem álcool e V de puro malte **não** entram como tendência

Não é critério desta etapa: Dagster, CI, SARIMAX, `marts_ml`, Power BI, `make export`.

## Tarefa 1 — testes `relationships`

Em [`transform/models/marts/core/_marts_core.yml`](../transform/models/marts/core/_marts_core.yml), colar FKs nativas do dbt nas colunas que apontam para chave **única** da dim:

| Coluna no fato | Dim | Campo |
| --- | --- | --- |
| `data_inicio` | `dim_data` | `data` |
| `metrica_id` | `dim_metrica` | `metrica_id` |
| `geografia_id` | `dim_geografia` | `geografia_id` |
| `categoria_id` | `dim_categoria_despesa` | `categoria_id` (`fct_substituicao_declarada`) |
| `recorte_id` | `dim_recorte_demografico` | `recorte_id` |

`dim_fonte` **não** é única em `source_id`. Não usar `relationships` em `source_id` sozinho. Criar teste genérico em [`transform/tests/generic/`](../transform/tests/generic/) (irmão de `unique_combination.sql`) no espírito `relationships_combination` para `(source_id, vintage_publicacao)` → `dim_fonte`. Aplicar nos fatos que carregam o par.

Não instalar `dbt_utils`. Não mudar o grain das fatos. `fonte_id` só entra se for coluna derivada extra, sem virar chave de negócio.

Se SIDRA tiver mês anterior a 2002, estender o spine de `dim_data` — não cortar a série. Se algum `recorte_id` / `categoria_id` do seed não estiver na dim, completar a dim; não relaxar o teste.

## Tarefa 2 — `qa_divergencias`

Grain ([`docs/grain.md`](grain.md)): **métrica × período × par de fontes/vintages**. Schema DuckDB: `marts_analytics`. Unique nessa chave. Relationships para `dim_metrica` e, se as colunas existirem, para `dim_fonte` (FK composta).

Conteúdo canônico em [`docs/fontes_lacunas.md`](fontes_lacunas.md) “Divergências já mapeadas”:

| Par | Como materializar |
| --- | --- |
| Produção 2024: 15,344 bi L (pub 2025) vs 17,211 bi L (pub 2026) | Derivado de `fct_mercado_cerveja_anual` (já existe) |
| Emprego apostas: IEPS 1.144 vs IBJR/ANJL 15,5 mil | Derivado de `fct_indicador_declarado` |
| Comércio exterior kg (2021–22) vs litros (2024+) | Contexto ADR 0002. Seed/citação **só** com página no extract dos Anuários 2021–2022. Não vira série do Ato 1 |
| Zero: 757 mi L MAPA vs ~702 mi L Euromonitor | MAPA citável (pub 2025 p. 55). Euromonitor só se o HTML do lake (`web_istoe_sem_alcool` / Catalisi) tiver o número. Sem chute |
| Apostadores 2025: Klavi 3,7 mi vs LAI ~25 mi | Klavi já no fato. LAI só se houver citação no acervo. Senão fica no papel — **não inventar** |
| Tamanho de mercado 2025: EE119 Pix vs Regulus US$ 4,1 bi | EE119 no fato. Regulus via `web_senado_mercado_global_bets_2026` se o extract HTML tiver o valor |

Colunas no espírito: `metrica_id`, período (`ano_referencia` e/ou `data_inicio`), `source_id_a`, `vintage_a`, `valor_a`, `unidade_a`, `source_id_b`, `vintage_b`, `valor_b`, `unidade_b`, `tipo_divergencia` (`vintage` / `unidade` / `definicao` / `amostra_vs_universo` / `fluxo_vs_receita`), `nota`. Unidade A pode diferir da B (esse é o ponto do par kg vs L).

Preferir SQL a partir dos fatos. Seed `seed_qa_divergencias` só para pares citáveis que **não** estão nos fatos. Inspecionar Parquet/HTML antes de seedar. Afirmação sem fonte primária no lake **não entra** ([`docs/fontes_lacunas.md`](fontes_lacunas.md)).

Não materializar GGR/SPA. Não emendar Euromonitor com MAPA como uma série.

## Tarefa 3 — `marts_analytics` (`agg_*`)

Nova pasta [`transform/models/marts/analytics/`](../transform/models/marts/analytics/) + schema `marts_analytics` em [`transform/dbt_project.yml`](../transform/dbt_project.yml). Unique na chave de grain. Relationships para as dims usadas. Janela analítica **2023–2026** nestes aggs (o histórico longo da 8885 permanece em `fct_serie_mensal` para o SARIMAX da etapa 8).

| Tabela | Grain | Conteúdo desta etapa |
| --- | --- | --- |
| `agg_panorama_mensal` | um mês | Ato 1. Pivot/join de `fct_serie_mensal` (8885 11.1, 8888, IPCA cerveja, rendimento real), filtro 2023–2026. Sem produção MAPA anual nesta tabela |
| `qa_divergencias` | métrica × período × par de fontes/vintages | Tarefa 2. Ato 1 |
| `agg_de_onde_saiu_o_dinheiro` | categoria × recorte | Ato 2. `fct_substituicao_declarada` (Locomotiva p. 19, inclusive 48% bares/restaurantes/delivery) |
| `agg_mix_produto` | ano ref × vintage × segmento | Ato 2. Estrutura e unique existem. **Não** popular sparkline 4,9%→1,27% nem V 29,2→24,7→29,2. Se houver ponto citável, marcar `usar_como_tendencia = false` (ou equivalente). Pode ficar vazia se não houver outro segmento citável sem ser tendência |
| `agg_estrutura_setorial` | setor × métrica | Ato 3. Emprego apostas (duas linhas, duas definições) a partir de `fct_indicador_declarado`. Sem GGR. Emprego/PIB cerveja só com citação no Anuário; senão não entra |
| `agg_indicadores_declarados` | fonte × métrica × período | Página de proveniência de `fct_indicador_declarado` (`pagina`, `citacao_textual`). Sem `ggr` / `destinacoes_legais` |

Nada de `marts_ml`. Nada de `make export` / `.pbix`.

## Tarefa 4 — docs (obrigatório)

Quando o critério de pronto fechar:

- [`docs/etapas.md`](etapas.md) — etapa atual **7**. Manter o link para este briefing
- [`docs/implementacao.md`](implementacao.md) — qualidade / `qa_divergencias` / `marts_analytics` no “Feito”
- [`transform/README.md`](../transform/README.md) — schema `marts_analytics`; FKs rodam no `dbt build`
- Este arquivo: no topo, marcar **feita** (não apagar o briefing)
- Uma linha na tabela de docs do [`README.md`](../README.md) apontando este briefing. Não expandir o README além disso. Não reescrever ADRs

**Não** alterar `docs/grain.md`.

## Fora de escopo

- Etapa 7: Dagster, `dagster-dbt`, GitHub Actions, Pages
- Etapa 8: SARIMAX, `fct_cerveja_previsao`, `marts_ml`
- Etapa 9–10: Power BI, `make export`, demo, Zenodo
- Mix sem álcool 4,9%→1,27% e V de puro malte 29,2→24,7→29,2 como tendência no dashboard (quebra metodológica / três vintages — [`docs/fontes_lacunas.md`](fontes_lacunas.md) “Verificações etapa 4”)
- Segundo modelo SARIMAX de cerveja zero
- Clima, SPA GGR, shift-share, GLP-1 como regressor (ADRs 0002–0004 e [`docs/trabalho_futuro.md`](trabalho_futuro.md))
- Commit/push só se o usuário pedir

## Verificação

```powershell
uv sync --extra dev
make dvc-pull
make test
make lint
make dbt-build
```

Se o lake local estiver vazio, `make dvc-pull` primeiro.

Conferir no DuckDB (ou `dbt show`):

- `dbt test` inclui `relationships` (e a FK composta para `dim_fonte`) e todos passam
- `qa_divergencias` tem o par 15,344 vs 17,211 de 2024
- `qa_divergencias` tem o par IEPS vs IBJR de emprego
- `agg_panorama_mensal` só 2023–2026 e 8885 só via fato 11.1
- `agg_de_onde_saiu_o_dinheiro` tem a linha 48% bares/restaurantes/delivery
- nenhum agg/fato com `metrica_id` `ggr` ou `destinacoes_legais`
- mix sem álcool / puro malte não aparecem como série de tendência

## Arquivos esperados (orientação)

Tocar no mínimo:

- `transform/dbt_project.yml`
- `transform/models/marts/core/_marts_core.yml` (relationships)
- `transform/tests/generic/` (FK composta → `dim_fonte`)
- `transform/models/marts/analytics/*.sql` e `*.yml`
- `transform/seeds/` só se um par de QA citável não vier dos fatos
- `transform/README.md`
- `docs/etapa_6.md` (status)
- `docs/etapas.md`
- `docs/implementacao.md`
- `README.md` (uma linha na tabela de docs)

Não tocar: `docs/grain.md`, `orchestration/`, `analysis/`, `exports/powerbi/`, código de ingest/extract salvo se um path de source estiver errado para um extract de QA.

# Briefing para o agente — etapa 5

**Status: a fazer.** Não avançar daqui para qualidade/`qa_divergencias`, Dagster, SARIMAX ou Power BI.

Cole o bloco abaixo num chat novo (Agent mode) e anexe este arquivo se quiser. O agente deve **executar** o briefing, não reescrever o plano.

```
Implemente a etapa 5 deste repositório. Siga docs/etapa_5.md até o critério de pronto.
Não avance para etapa 6 (qa_divergencias / relationships), Dagster, SARIMAX, Power BI ou Zenodo.
Não altere docs/grain.md.
```

---

## Contexto do projeto

`bets-cerveja` é um **pipeline de pesquisa**, não um app de apostas. Pergunta: de onde saiu o dinheiro das bets no Brasil (2023–2026), em especial o canal on-premise (bares/restaurantes/delivery). Cerveja agregada não caiu; a ponte empírica é o survey Locomotiva (48% C/D/E dizem ter tirado dinheiro de bares/restaurantes/delivery).

Ordem fixa em [`docs/etapas.md`](etapas.md). Etapas **1–4 feitas**. Esta tarefa é **só a etapa 5**. Grain em [`docs/grain.md`](grain.md) — **não alterar**. Arquitetura: [`docs/architecture.md`](architecture.md). Matriz de afirmações: [`docs/fontes_lacunas.md`](fontes_lacunas.md). Métricas: [`docs/data_dictionary.md`](data_dictionary.md) e [`conf/metrics.yml`](../conf/metrics.yml).

Stack já no repo: Python 3.12 (`requires-python = ">=3.12,<3.13"`), `uv`, Typer, Parquet, DVC → R2, pandera. **dbt/DuckDB ainda não existem** (`transform/` é só README).

Numeração antiga vs canônica: docs antigos dizem “Fase 3 = dbt” e “Fase 5 = Dagster” ([ADR 0001](adr/0001-orquestracao-dagster-em-vez-de-airflow.md), [`orchestration/README.md`](../orchestration/README.md), [`docs/architecture.md`](architecture.md)). Ignorar. **Dagster é etapa 7.** Não instalar Dagster nesta etapa.

## Estado atual do código

| Camada | Status |
| --- | --- |
| `conf/sources.yml` + CLI `sources` | pronto |
| Ingest HTTP/SIDRA/BCB → `data/00_landing` + `_manifest.jsonl` | pronto |
| Extract PDF/HTML → `data/01_raw/<dominio>/<id>/extract.parquet` (`RawExtract`) | pronto |
| Extract API SIDRA/BCB → mesmo path (`RawApiSeries`) | pronto (etapa 4) |
| `transform/` dbt | **falta** — só [`transform/README.md`](../transform/README.md) |
| `pyproject.toml` | sem `dbt-duckdb` / `dbt-core` |
| Makefile | `sources`, `test`, `lint`, `ingest`, `extract`, `dvc-*`; **sem** `dbt-build` |
| Dagster, SARIMAX, Power BI | fora de escopo desta etapa |

Lake versionado por DVC (`data/00_landing.dvc`, `data/01_raw.dvc`). Diretórios ignorados pelo git. Se não existirem no disco: `make dvc-pull`. Warehouse DuckDB já está no `.gitignore` (`*.duckdb`, `warehouse/`). Artefatos dbt também (`transform/target/`, `transform/logs/`).

Schemas em [`src/betscerveja/schemas/raw.py`](../src/betscerveja/schemas/raw.py):

- `RawExtract` (PDF/HTML): `source_id`, `metodo`, `pagina`, `trecho`, `tabela_idx`, `celulas_json`
- `RawApiSeries` (SIDRA/BCB): `source_id`, `metodo`, `periodo`, `localidade_*`, `variavel_*`, `classificacao_*`, `categoria_*`, `valor`, `unidade`

Destino do extract: `data/01_raw/<dominio>/<id>/extract.parquet`. Domínios: `cerveja`, `apostas`, `macro`.

IDs de API (série tidy — entram em `fct_serie_mensal`):

- `sidra_8885_pim_bebidas` — classificação 542; **usar só 11.1** (`categoria_id=129192`) para `producao_bebidas_alcoolicas_indice`. 11.2 (`129193`) não vai para essa métrica. Cerveja zero **entra em 11.1** (CONCLA 1113-5/02); não criar série própria
- `sidra_8888_pim_geral` — PIM-PF geral (Brasil)
- `sidra_7060_ipca` — variável 63; **filtrar item cerveja** (classificação 315) no dbt, não na extração
- `bcb_sgs_rendimento_real` — SGS 24364; `periodo` = data do ponto; classificação nula

IDs de Anuário (produção anual — entram em `fct_mercado_cerveja_anual`; vintage na chave):

- `anuario_cerveja_ref2023_pub2024` — produção 2023 = 15.361.344.112,77 L
- `anuario_cerveja_ref2024_pub2025` — produção 2024 original = 15.344.065.267,36 L (p. 49)
- `anuario_cerveja_ref2025_pub2026` — produção 2024 retificada = 17.210.754.610,75 L (p. 7 e p. 51); produção 2025 = 15.688.083.191,69 L

IDs para fatos declarados / substituição (esparsos):

- `strategy_impacto_apostas_consumo_2024` — Locomotiva p. 19 (eixo do projeto)
- `bcb_ee119_apostas_2024` — Pix / PBF, um mês (ago/2024)
- `fundaj_nt39_pce_2024`, `ieps_dossie_bets_saude`, `lca_ibjr_anjl_panorama_apostas_2025`
- `web_klavi_placar_bets` / `web_valor_klavi_apostadores_2026` — amostra, não censo

`spa_panorama_apostas_2025` está `fora_de_escopo`. **Não** criar `fct_apostas_oficial` (ADR 0004).

## Critério de pronto

`dbt build` materializa o **star schema** (`marts_core`) em DuckDB. Testes `unique` nas chaves compostas de [`docs/grain.md`](grain.md) passam. `make test` e `make lint` continuam verdes.

Pronto quando:

1. `make dbt-build` (ou equivalente) roda sem erro
2. Existem as dims e fatos listados em grain.md sob `marts_core` (ver Tarefa 4)
3. `fct_serie_mensal` tem SIDRA 8885 categoria 11.1, IPCA cerveja e rendimento real
4. `fct_mercado_cerveja_anual` tem as duas produções de 2024 (vintages 2025 e 2026) como linhas distintas
5. `ggr` / `destinacoes_legais` **não** aparecem como linhas de fato (podem existir em `dim_metrica`)
6. Mix sem álcool e V de puro malte **não** entram como tendência no mart

Não é critério desta etapa: `qa_divergencias`, testes `relationships`, `marts_analytics` (`agg_*`), `marts_ml`.

## Tarefa 1 — scaffolding dbt-duckdb

1. Adicionar `dbt-core` + `dbt-duckdb` no extra `dev` de [`pyproject.toml`](../pyproject.toml) (Python 3.12). `uv sync --extra dev`.
2. Projeto em [`transform/`](../transform/):
   - `dbt_project.yml` (nome `betscerveja`)
   - `profiles.yml` no mesmo diretório: DuckDB em `warehouse/betscerveja.duckdb` (path relativo à raiz do repo ou a `transform/`; o diretório `warehouse/` já está no `.gitignore`)
   - `models/staging/`, `models/intermediate/`, `models/marts/core/`
   - `seeds/`
   - `models/sources.yml` (ou `models/staging/_sources.yml`)
3. Sources dbt leem Parquet via `external_location` do `dbt-duckdb`. Variável `raw_root` apontando para `data/01_raw`. Um source/tabela por extract usado, path `data/01_raw/<dominio>/<id>/extract.parquet`.
4. Makefile: alvo `dbt-build` no espírito de `cd transform && uv run dbt build --profiles-dir .`. Incluir `dbt-build` no `.PHONY`.
5. [`transform/README.md`](../transform/README.md): dbt entra **nesta** etapa (5), não “Fase 3”. Como rodar. Não instalar `dbt_utils` só para spine de datas — gerar `dim_data` em SQL DuckDB.

## Tarefa 2 — seeds (catálogo, não número inventado)

- `seed_metricas` ← [`conf/metrics.yml`](../conf/metrics.yml) → base de `dim_metrica` (`metrica_id` = `id` do YAML)
- `seed_fontes` ← [`conf/sources.yml`](../conf/sources.yml): `source_id`, `vintage_publicacao`, `tier_confiabilidade`, `e_oficial`, `ano_referencia` → base de `dim_fonte`. Sem `vintage_publicacao` não dá para representar as duas produções de 2024
- `seed_citacoes` — **só** para indicadores esparsos de PDF/HTML que não são série tidy. Colunas no espírito: `source_id`, `metrica_id`, `periodo` / `ano_referencia`, `valor`, `unidade`, `pagina`, `citacao_textual`, `geografia` / `recorte` / `categoria_despesa` conforme o fato. Copiar da matriz em [`docs/fontes_lacunas.md`](fontes_lacunas.md), com página. Não chutar número que não esteja citável

`seed_citacoes` **não** é atalho para SIDRA/BCB. **Não** é atalho para produção MAPA se o Parquet do Anuário (`metodo=pdfplumber_table`) parsear. Fallback de citação para o Anuário só depois de inspecionar `celulas_json` e comprovar que está ilegível **nessas páginas**.

Citações mínimas a materializar (Ato 2 / Ato 3, grain `fct_indicador_declarado` e `fct_substituicao_declarada`):

- Locomotiva / Strategy& p. 19: 52% poupança; 48% bares/restaurantes/delivery; 43% roupas; 41% cultura (classes C/D/E). Métrica `substituicao_categoria_despesa`
- EE119: ~R$ 20 bi/mês fluxo Pix (ago/2024); 5 mi beneficiários PBF, R$ 3 bi. Métrica `fluxo_bruto_apostado` / recorte PBF. Um mês, não série
- Klavi: 3,7 mi apostadores em 2025 (amostra Open Finance, não censo)
- IEPS ~1.144 empregos formais vs IBJR/ANJL 15,5 mil — duas linhas declaradas, não um número único

Não materializar GGR oficial nem destinações de 12%. Não afirmar MindMiners/Scanntech (fonte primária ausente / fora do modelo).

## Tarefa 3 — staging e intermediate

Staging: 1:1 com o Parquet, **sem** regra de negócio. No mínimo:

- `stg_raw_api_*` (ou union) para as 4 APIs — colunas de `RawApiSeries`
- `stg_raw_pdf` para Anuários (e PDFs usados nas citações, se for parsear) — colunas de `RawExtract`

Intermediate:

1. Período SIDRA `YYYYMM` → primeiro dia do mês (`data_inicio`). BCB SGS: parse da data do ponto (formato típico `DD/MM/YYYY` no JSON) → `data_inicio`
2. SIDRA 8885: filtrar `categoria_id = '129192'` para `producao_bebidas_alcoolicas_indice`
3. SIDRA 7060: filtrar o item cerveja na classificação 315 (inspecionar `categoria_nome` / `categoria_id` no Parquet local; não adivinhar o código sem ler o extract)
4. Fatos mensais/anuais apontam para o **primeiro dia** do período em `dim_data` e carregam `granularidade_periodo` (`mes` / `ano`) como atributo degenerado — regra de [`docs/grain.md`](grain.md)
5. Anuário → litros de produção nacional: filtrar `source_id` + `pagina` citados na etapa 4; parsear `celulas_json`. Se ilegível, fallback `seed_citacoes` **com a mesma citação** (página). Não interpolar, não emendar Euromonitor, não usar Anuários 2021–2022 como série do Ato 1 (ADR 0002; só contexto)

Janela analítica dos marts: 2023–2026. SIDRA pode ter histórico mais longo no staging (o SARIMAX da etapa 8 treina nisso); o fato pode guardar o histórico mensal — não cortar a série 8885 em 2023 no raw.

## Tarefa 4 — `marts_core` (star schema)

Implementar **todas** as tabelas de grain em `marts_core`. Não criar `marts_analytics` nem `marts_ml`.

Dimensões:

| Tabela | Grain / chave | Notas |
| --- | --- | --- |
| `dim_data` | um dia; chave `data` | Spine SQL. Cobre no mínimo o histórico SIDRA até 2026-12-31 |
| `dim_geografia` | `nivel` + `codigo` | Pelo menos Brasil. Não exigir UF se o raw só tiver N1 |
| `dim_fonte` | `source_id` + `vintage_publicacao` | |
| `dim_metrica` | `metrica_id` | Separa `fluxo_bruto_apostado`, `ggr`, `destinacoes_legais` |
| `dim_segmento_produto` | teor + puro_malte + estilo | Dimensão de apoio; **não** popular fato de mix como tendência |
| `dim_categoria_despesa` | `categoria_id` | Poupança, bares/restaurantes/delivery, roupas, cultura, … |
| `dim_recorte_demografico` | hash dos atributos | Pelo menos C/D/E e PBF se usados nos fatos |

Fatos:

| Tabela | Chave | Conteúdo desta etapa |
| --- | --- | --- |
| `fct_serie_mensal` | `data_inicio`, `metrica_id`, `geografia_id` | 8885 11.1, 8888, IPCA cerveja, rendimento real |
| `fct_mercado_cerveja_anual` | ano ref × **vintage** × UF (Brasil se não houver UF) | Produção MAPA em litros; duas linhas para 2024 |
| `fct_indicador_declarado` | fonte × métrica × período × geografia × recorte; inclui `pagina` e `citacao_textual` | EE119, Klavi, IEPS, IBJR, etc. Sem fato “oficial” de apostas |
| `fct_substituicao_declarada` | fonte × categoria de despesa × recorte | Locomotiva p. 19 — eixo do projeto |

Contrato dbt + teste `unique` na chave composta de **cada** tabela acima. `not_null` nas chaves é bem-vindo.

Não adicionar testes `relationships` nem o model `qa_divergencias` — isso é etapa 6. A divergência 15,344 vs 17,211 bi L de 2024 **já fica representável** pelas duas linhas de `fct_mercado_cerveja_anual`; não precisa da tabela de QA agora.

## Tarefa 5 — docs (obrigatório)

Quando o critério de pronto fechar:

- [`docs/etapas.md`](etapas.md) — etapa atual **6**. Manter o link para este briefing
- [`docs/implementacao.md`](implementacao.md) — dbt no “Feito”; comando `make dbt-build` (e `make dvc-pull` antes se o lake estiver vazio)
- [`docs/data_dictionary.md`](data_dictionary.md) — seed `dim_metrica` já existe (tirar “Na Fase 3 vira seed… Até lá”)
- [`transform/README.md`](../transform/README.md) — como na Tarefa 1
- Este arquivo: no topo, marcar **feita** (não apagar o briefing)
- Uma linha na tabela de docs do [`README.md`](../README.md) apontando este briefing. Não expandir o README além disso. Não reescrever ADRs

**Não** alterar `docs/grain.md`.

## Fora de escopo

- Etapa 6: `qa_divergencias`, testes `relationships`, `marts_analytics` (`agg_panorama_mensal`, `agg_de_onde_saiu_o_dinheiro`, `agg_mix_produto`, …)
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
make extract
make test
make lint
make dbt-build
```

Se o lake local estiver vazio, `make dvc-pull` primeiro. Extract das 4 APIs se os Parquets de API não existirem (`make extract`). Extract dos Anuários se for parsear produção a partir do PDF:

```powershell
uv run betscerveja extract --source anuario_cerveja_ref2023_pub2024
uv run betscerveja extract --source anuario_cerveja_ref2024_pub2025
uv run betscerveja extract --source anuario_cerveja_ref2025_pub2026
```

Conferir no DuckDB (ou `dbt show`):

- `fct_mercado_cerveja_anual` tem 2024 duas vezes (vintage 2025 e 2026) com 15.344… L e 17.210… L
- `fct_serie_mensal` para `producao_bebidas_alcoolicas_indice` só categoria 11.1
- `fct_substituicao_declarada` tem a linha 48% bares/restaurantes/delivery com `pagina` 19
- nenhum fato com `metrica_id` `ggr` ou `destinacoes_legais`

## Arquivos esperados (orientação)

Tocar no mínimo:

- `pyproject.toml` / `uv.lock`
- `Makefile`
- `transform/dbt_project.yml`
- `transform/profiles.yml`
- `transform/models/**/*.sql` e `*.yml` (sources, schema tests)
- `transform/seeds/`
- `transform/README.md`
- `docs/etapa_5.md` (status)
- `docs/etapas.md`
- `docs/implementacao.md`
- `docs/data_dictionary.md`
- `README.md` (uma linha na tabela de docs)

Não tocar: `docs/grain.md`, `orchestration/`, `analysis/`, `exports/powerbi/`, código de ingest/extract salvo se um path de source estiver errado.

# Briefing para o agente — etapa 10

**Status: feita** (critério de pronto fechado). Última etapa numerada. Não emitir DOI nem chamar a API do Zenodo.

Cole o bloco abaixo num chat novo (Agent mode) e anexe este arquivo se quiser. O agente deve **executar** o briefing, não reescrever o plano.

```
Implemente a etapa 10 deste repositório. Siga docs/etapa_10.md até o critério de pronto.
Não emita DOI, não peça token Zenodo e não chame a API do Zenodo.
Não altere docs/grain.md.
Não reescreva os ADRs 0001–0005.
Não instale Power BI, Streamlit, Plotly nem Vega.
Não publique figuras no GitHub Pages.
```

---

## Contexto do projeto

`bets-cerveja` é um **pipeline de pesquisa**, não um app de apostas. Pergunta: de onde saiu o dinheiro das bets no Brasil (2023–2026), em especial o canal on-premise (bares/restaurantes/delivery). Cerveja agregada não caiu; a ponte empírica é o survey Locomotiva (48% C/D/E dizem ter tirado dinheiro de bares/restaurantes/delivery).

Ordem fixa em [`docs/etapas.md`](etapas.md). Etapas **1–9 feitas**. Esta tarefa é **só a etapa 10** (demo local + pacote Zenodo). Grain em [`docs/grain.md`](grain.md) — **não alterar**. Arquitetura: [`docs/architecture.md`](architecture.md). Decisão de apresentação: [ADR 0005](adr/0005-figuras-em-vez-de-power-bi.md). Briefing da etapa 9 (já executado): [`docs/etapa_9.md`](etapa_9.md).

O demo mostra os três atos a partir de uma fatia commitada, **sem Cloudflare R2**. O Zenodo publica o **dataset derivado** (Parquet dos marts + PNG + atribuição), não os PDFs/HTML de `data/00_landing`. GitHub Pages **continua só o catálogo dbt**.

Stack: Python 3.12 (`requires-python = ">=3.12,<3.13"`), `uv`, Typer, Parquet, DVC → R2, pandera, dbt-duckdb, Dagster, statsmodels, matplotlib. Warehouse em `warehouse/betscerveja.duckdb` (gitignored). Apresentação: PNG + HTML em [`exports/figures/`](../exports/figures/). Sem `.pbix`, sem Power BI Desktop, sem Streamlit, sem Plotly, sem Vega.

Se `make figures` ainda não existir ou `exports/figures/` não tiver os cinco PNG + `index.html`, **parar** e executar a etapa 9 primeiro.

## Estado atual do código

| Camada | Status |
| --- | --- |
| Lake DVC (`00_landing`, `01_raw`) | pronto |
| `transform/` dbt-duckdb | **pronto (etapas 5–6)** |
| SARIMAX / `marts_ml` | **pronto (etapa 8)** |
| Dagster + CI + Pages | **pronto (etapa 7)** — `make ci` = lint → test → dvc-pull → dbt-build → sarimax. Pages = catálogo dbt |
| Figuras matplotlib | **pronto (etapa 9)** — `make figures` → `exports/figures/` |
| [`data/sample/`](../data/sample/) | só README (“vazia até existir extração”) |
| CLI `demo` / `make demo` | **não existem** |
| `exports/zenodo/` | **não existe** |
| `CITATION.cff` / `.zenodo.json` | **não existem** |
| Power BI / Streamlit / Plotly | fora de escopo |

Path do DuckDB: [`transform/profiles.yml`](../transform/profiles.yml) (`warehouse/betscerveja.duckdb`, override `BETSCERVEJA_DUCKDB_PATH`). Variável dbt `raw_root` default `data/01_raw` ([`transform/dbt_project.yml`](../transform/dbt_project.yml)); o Dagster já passa `--vars raw_root=...` em [`orchestration/assets_dbt.py`](../orchestration/assets_dbt.py).

Os sete Parquets que o dbt lê estão em [`transform/models/staging/_sources.yml`](../transform/models/staging/_sources.yml):

- `cerveja/sidra_8885_pim_bebidas/extract.parquet`
- `cerveja/sidra_8888_pim_geral/extract.parquet`
- `macro/sidra_7060_ipca/extract.parquet`
- `macro/bcb_sgs_rendimento_real/extract.parquet`
- `cerveja/anuario_cerveja_ref2023_pub2024/extract.parquet`
- `cerveja/anuario_cerveja_ref2024_pub2025/extract.parquet`
- `cerveja/anuario_cerveja_ref2025_pub2026/extract.parquet`

`spa_panorama_apostas_2025` está `fora_de_escopo`. **Não** criar `fct_apostas_oficial`. **Não** plotar `agg_mix_produto`. **Não** republicar bytes de `00_landing`.

A etapa 7 proibiu sample commitado para mascarar `dvc pull` na CI. Isso **permanece**: o job CI continua `dvc pull` + `01_raw`. Sample é só para `make demo`.

## Critério de pronto

`make demo` (sem `make dvc-pull`) materializa warehouse + forecast a partir de `data/sample/`, grava as figuras e monta `exports/zenodo/`. `make test` e `make lint` continuam verdes. CI **não** passa a publicar figuras, DuckDB nem lake. Pages continua só o catálogo dbt.

Pronto quando:

1. Os sete `extract.parquet` que o dbt lê estão commitados em `data/sample/` com a **mesma árvore** de `data/01_raw/`. São dados derivados ([`LICENSE-DATA`](../LICENSE-DATA), CC BY 4.0), **não** bytes de `00_landing`.
2. A série SIDRA/BCB no sample é a série **cheia** (treino SARIMAX é pré-2023). “Fatia pequena” = Parquet extraído em vez de PDF/HTML do lake, não um recorte 2023–2026.
3. Função importável (ex. [`src/betscerveja/demo.py`](../src/betscerveja/demo.py)) faz, nesta ordem: `dbt build --vars raw_root=data/sample` → `run_forecast` → `render_figures` → pacote Zenodo. CLI e Make **chamam essa função** — não duplicar o pipeline.
4. `make demo` no Makefile (`.PHONY`). **Não** encadear em `make ci`. Não disparar ingest/extract/rede.
5. `exports/zenodo/` contém pelo menos:
   - README de atribuição (MAPA, IBGE, BCB, Locomotiva, etc.)
   - `LICENSE-DATA`
   - PNG + `index.html` (os da etapa 9)
   - Parquet dos marts de apresentação: `agg_panorama_mensal`, `fct_mercado_cerveja_anual`, `fct_cerveja_previsao`, `agg_de_onde_saiu_o_dinheiro`, `agg_estrutura_setorial`, `qa_divergencias`, `agg_indicadores_declarados`, `ml_metricas`, `ml_coeficientes`
   - metadados (`.zenodo.json` e/ou `CITATION.cff` com DOI placeholder `https://doi.org/10.5281/zenodo.XXXX`)
6. Pytest barato: sample tem os sete paths; a função de empacotar escreve o manifesto em tmp. **Sem** dbt+SARIMAX no pytest. Sem rede. Sem UI Dagster.
7. Docs da etapa 7 (“não inventar sample na CI”) continuam válidos: o job CI segue `dvc pull` + `01_raw`.

Não é critério desta etapa: DOI já emitido, upload pela API Zenodo, segundo job Pages, Dagster job de demo, servir HTTP, abrir o browser.

## Tarefa 1 — sample commitado

1. Script único (ex. [`scripts/sync_sample.py`](../scripts/sync_sample.py)) copia os sete Parquets de `data/01_raw` → `data/sample`. Quem mantém o lake roda isso **uma vez** depois de `dvc pull` / extract. O agente que executar este briefing precisa dos Parquets no disco (se `01_raw` estiver vazio: `make dvc-pull`; se ainda não houver extract: `make extract`). Depois commita o conteúdo de `data/sample/` (não o de `01_raw`).
2. [`.gitignore`](../.gitignore) já ignora `data/01_raw/*` e **não** ignora `data/sample/` — manter sample versionado. Não adicionar `data/sample/` ao gitignore.
3. [`data/sample/README.md`](../data/sample/README.md): deixar de dizer “vazia”; explicar que é para `make demo` sem R2; CI não usa esta pasta.
4. Não commitar PDF/HTML de `00_landing`.

Se `01_raw` não existir no disco e o DVC falhar, **parar** e dizer isso. Não inventar Parquet sintético no sample.

## Tarefa 2 — `make demo`

1. Código em [`src/betscerveja/demo.py`](../src/betscerveja/demo.py) (criar; nome equivalente ok). Função importável: valida os sete paths em `data/sample/`; roda `dbt build` com `--vars raw_root` apontando para `data/sample` (mesmo padrão de [`orchestration/assets_dbt.py`](../orchestration/assets_dbt.py)); chama `run_forecast` e `render_figures` já existentes; empacota Zenodo (tarefa 3).
2. DuckDB: mesmo `BETSCERVEJA_DUCKDB_PATH` / `warehouse/betscerveja.duckdb`.
3. Comando `betscerveja demo` em [`src/betscerveja/cli.py`](../src/betscerveja/cli.py).
4. [`Makefile`](../Makefile): alvo `demo` no espírito de `uv run betscerveja demo`. Incluir no `.PHONY`. **Não** colocar `demo` (nem `figures`) na receita de `ci`.
5. Se algum `data/sample/.../extract.parquet` faltar, falhar com mensagem apontando o README do sample — **não** cair para `01_raw` em silêncio (senão o demo deixa de ser o contrato sem DVC).
6. Ao terminar, imprimir o path de `exports/figures/index.html` e de `exports/zenodo/`. Sem `http.server`, sem Streamlit, sem abrir o browser.

Reusar `run_forecast` e `render_figures`. Não reimplementar SARIMAX nem matplotlib.

## Tarefa 3 — Zenodo (código + ação sua)

Código:

1. Empacotar só derivado em `exports/zenodo/`. Sem DuckDB, sem `.env`, sem lake DVC, sem `00_landing`.
2. `.zenodo.json` e `CITATION.cff` na raiz do repo (e/ou cópia no pacote): título, autor (Kaynan, como em [`pyproject.toml`](../pyproject.toml)), descrição curta do README, licença dados CC-BY-4.0, código MIT, related identifier = URL do GitHub. DOI = `https://doi.org/10.5281/zenodo.XXXX` até o usuário reservar o recorde.
3. README do pacote: o que é cada arquivo; ponte Locomotiva 48% é survey, não substituição litro a litro; mix sem álcool / puro malte fora do gráfico; bytes originais continuam sob a licença de cada publicador.

Ação **sua** (externa, como secrets R2 na etapa 7) — o agente **documenta** em [`docs/implementacao.md`](implementacao.md), **não** pede token no chat e **não** chama a API:

1. Conta Zenodo (sandbox primeiro se quiser).
2. Upload da pasta `exports/zenodo/` pelo site.
3. Reservar/publicar DOI e colar em `CITATION.cff` + README num commit posterior.

[`docs/trabalho_futuro.md`](trabalho_futuro.md): tirar Zenodo da lista “não criar até existir dataset”; o dataset passa a existir nesta etapa. O DOI em si continua ação externa.

## Tarefa 4 — docs (obrigatório)

Quando o critério de pronto fechar:

- [`docs/etapas.md`](etapas.md) — etapa atual **fim** (não há etapa 11). Manter o link para este briefing.
- [`docs/implementacao.md`](implementacao.md) — demo/Zenodo no “Feito”; `make demo` nos comandos; esvaziar “Ainda não”; nas “Ações suas”: upload Zenodo + DOI (além dos secrets R2 / Pages que já estão).
- [`README.md`](../README.md) — uma linha na tabela de docs apontando este briefing; `make demo` no quickstart (uma linha, não um tutorial).
- [`data/README.md`](../data/README.md) e [`data/sample/README.md`](../data/sample/README.md)
- [`exports/figures/README.md`](../exports/figures/README.md) — `make demo` de fato existe
- [`docs/architecture.md`](architecture.md) — uma linha: demo local na etapa 10; Pages inalterado. Não reverter figuras → Power BI.
- Este arquivo: no topo, marcar **feita** (não apagar o briefing)

**Não** alterar `docs/grain.md`. **Não** reescrever ADRs 0001–0005. **Não** reabrir Power BI.

## Fora de escopo

- Power BI, `.pbix`, Streamlit, Dash, Plotly, Vega
- Segundo GitHub Pages com as figuras; MkDocs paralelo
- Encadear `demo` ou `figures` em `make ci`
- Publicar `00_landing`, DuckDB ou `.env` no Zenodo ou no Pages
- Upload automático Zenodo, token no chat, Dagster Cloud, Dagster job de demo
- Plotar `agg_mix_produto`; mix sem álcool 4,9%→1,27% e V de puro malte como tendência
- Segundo modelo SARIMAX de cerveja zero
- Clima, SPA GGR, shift-share, GLP-1 como regressor (ADRs 0002–0004)
- Servir HTTP / abrir o browser como critério
- Commit/push só se o usuário pedir

## Verificação

```powershell
uv sync --extra dev
# sem make dvc-pull no caminho do demo
make demo
make test
make lint
```

Conferir em `data/sample/`:

- os sete `extract.parquet` existem, mesma árvore de `01_raw`
- SIDRA 8885 / BCB têm meses **antes** de 2023
- nenhum PDF/HTML de landing

Conferir em `exports/figures/`:

- os cinco PNG e o `index.html` existem depois do demo

Conferir em `exports/zenodo/`:

- Parquet dos marts listados no critério
- PNG + `index.html`
- `LICENSE-DATA` e README de atribuição
- metadados com DOI placeholder (não um DOI inventado como se fosse real)

Conferir no Makefile / CI:

- `demo` está no `.PHONY` e **não** está na receita de `ci`
- job de Pages continua só com `dbt docs` (sem PNG, sem DuckDB, sem `exports/zenodo`)

## Arquivos esperados (orientação)

Tocar no mínimo:

- `scripts/sync_sample.py` (ou equivalente)
- `data/sample/` (sete Parquets + README)
- `src/betscerveja/demo.py` (ou equivalente)
- `src/betscerveja/cli.py`
- `Makefile` (`demo` no `.PHONY`; **não** em `ci`)
- `exports/zenodo/` (README + LICENSE-DATA + Parquet + figuras copiadas)
- `CITATION.cff` e/ou `.zenodo.json`
- `tests/`
- `docs/etapa_10.md` (status)
- `docs/etapas.md`
- `docs/implementacao.md`
- `docs/architecture.md` (uma linha)
- `docs/trabalho_futuro.md` (Zenodo)
- `README.md` (uma linha na tabela + `make demo` no quickstart)
- `data/README.md`, `data/sample/README.md`, `exports/figures/README.md`

Não tocar: `docs/grain.md`, ADRs 0001–0005, `analysis/` como fonte da verdade, models dbt (salvo `raw_root` via `--vars`), código de ingest/extract, o fit SARIMAX (chamar a função já existente), o job Pages (não adicionar figuras).

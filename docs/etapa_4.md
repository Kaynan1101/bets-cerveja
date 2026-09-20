# Briefing para o agente — etapa 4

**Status: feita** (critério de pronto fechado). Não avançar daqui para dbt/Dagster/SARIMAX.

Cole o bloco abaixo num chat novo (Agent mode) e anexe este arquivo se quiser. O agente deve **executar** o briefing, não reescrever o plano.

```
Implemente a etapa 4 deste repositório. Siga docs/etapa_4.md até o critério de pronto.
Não avance para dbt, Dagster, SARIMAX, Power BI ou Zenodo.
```

---

## Contexto do projeto

`bets-cerveja` é um **pipeline de pesquisa**, não um app de apostas. Pergunta: de onde saiu o dinheiro das bets no Brasil (2023–2026), em especial o canal on-premise (bares/restaurantes/delivery). Cerveja agregada não caiu; a ponte empírica é o survey Locomotiva (48% C/D/E dizem ter tirado dinheiro de bares/restaurantes/delivery).

Ordem fixa em [`docs/etapas.md`](etapas.md). Etapas **1–3 feitas**. Esta tarefa é **só a etapa 4**. Grain em [`docs/grain.md`](grain.md) — **não alterar** (contrato da etapa 5).

Stack: Python 3.12, `uv`, Typer, Parquet, DVC → R2, pandera. dbt/DuckDB ainda não existem (`transform/` é README).

## Estado atual do código

| Camada | Status |
| --- | --- |
| `conf/sources.yml` + CLI `sources` | pronto |
| Ingest HTTP/SIDRA/BCB → `data/00_landing` + `_manifest.jsonl` | pronto |
| Extract PDF/HTML → `data/01_raw/.../extract.parquet` | pronto |
| Extract `tipo: api` (SIDRA/BCB JSON) | **falta** — `extract/runner.py` levanta `ValueError` |
| dbt, Dagster, SARIMAX, Power BI | fora de escopo desta etapa |

Lake versionado por DVC (`data/00_landing.dvc`, `data/01_raw.dvc`). Diretórios ignorados pelo git. Se não existirem no disco: `make dvc-pull`.

IDs relevantes:

- APIs: `sidra_8885_pim_bebidas`, `sidra_8888_pim_geral`, `sidra_7060_ipca`, `bcb_sgs_rendimento_real`
- Anuários de mix: `anuario_cerveja_ref2023_pub2024`, `anuario_cerveja_ref2024_pub2025`, `anuario_cerveja_ref2025_pub2026`

SIDRA 8885 já puxa `classificacao=542[129192,129193]` (notas em `conf/sources.yml`: 129192 = 11.1 alcoólicas, 129193 = 11.2 não alcoólicas). Cerveja zero ainda não classificada entre as duas.

## Critério de pronto

Três perguntas respondidas **com citação** (página, categoria SIDRA, ou célula extraída) em [`docs/fontes_lacunas.md`](fontes_lacunas.md):

1. Onde o IBGE classifica cerveja sem álcool na SIDRA 8885 — **11.1** (`129192`) ou **11.2** (`129193`)?
2. Por que a participação sem álcool cai **4,9% → 1,27%** no Anuário?
3. Por que puro malte faz **29,2% → 24,7% → 29,2%**?

Mais: `uv run betscerveja extract --source sidra_8885_pim_bebidas` escreve Parquet; `make test` e `make lint` passam.

## Tarefa 1 — extract de API (código)

Hoje [`src/betscerveja/extract/runner.py`](../src/betscerveja/extract/runner.py) só aceita pdf/html:

```python
else:
    raise ValueError(f"{source.id}: extração só para pdf/html")
```

Landing SIDRA/BCB é `payload.json`. Sem série tidy não dá para inspecionar a 8885 nem alimentar dbt depois.

Fazer:

1. Schema pandera novo `RawApiSeries` em [`src/betscerveja/schemas/raw.py`](../src/betscerveja/schemas/raw.py), **separado** de `RawExtract` (PDF/HTML). Colunas no espírito:
   - `source_id`, `metodo`
   - `periodo`
   - `localidade_id`, `localidade_nome`
   - `variavel_id`, `variavel_nome`
   - `classificacao_id`, `classificacao_nome`
   - `categoria_id`, `categoria_nome`
   - `valor`, `unidade`
   - campos SIDRA-only podem ser nulos no BCB (e vice-versa). Coerce com pandera.
2. `extract_sidra` e `extract_bcb` no runner, despacho por `source.adapter` (`api_sidra` / `api_bcb`). Destino já previsto: `data/01_raw/<dominio>/<id>/extract.parquet`.
3. SIDRA API v3 é JSON aninhado (`variaveis` → `resultados` → `series` → `serie` como mapa período→valor). Achatar. Valores `"..."` / `"-"` viram nulo, não string.
4. BCB SGS: lista `[{data, valor}]`. `periodo` = data da série; classificação/categoria nulas.
5. Testes **sem rede** em `tests/` com fixtures JSON mínimas (SIDRA aninhado + SGS).
6. CLI `betscerveja extract --source <id>` já existe — só precisa despachar API.
7. Makefile: alvo `extract` para as 4 APIs. **Deduplicar** regras `sources` / `test` / `lint` / `dvc-*` que estão repetidas.

Não instalar dbt. Não criar `transform/models`.

## Tarefa 2 — pergunta 1 (SIDRA 8885)

Ler metadados e/ou payload local da 8885. Endpoint público de metadados (só se o JSON local não bastar): `https://servicodados.ibge.gov.br/api/v3/agregados/8885/metadados`. Não inventar fonte nova em `sources.yml` só por isso.

Hipótese a **confirmar**, não gravar de antemão: PIM-PF classifica o **estabelecimento** (CNAE). Cerveja zero produzida em cervejaria tende a ficar em **11.1**, não em refrigerantes (11.2).

Se 11.1 **incluir** zero álcool: série própria no SARIMAX continua fora de escopo ([`docs/trabalho_futuro.md`](trabalho_futuro.md)). Se **excluir**: anotar isso — ainda **não** implementar segundo modelo.

Implicação para `producao_bebidas_alcoolicas_indice` em [`docs/data_dictionary.md`](data_dictionary.md): só editar se a métrica deixar de significar “índice de bebidas alcoólicas ≈ produção de cerveja com álcool”.

## Tarefa 3 — perguntas 2 e 3 (Anuários)

Não chutar. Usar Parquets já extraídos (`metodo=pdfplumber_table`) dos três Anuários. Procurar células de mix (sem álcool, puro malte). Citar página (`pagina`) e, se útil, `tabela_idx`.

Cruzar com a retificação de produção 2024 já na matriz:

- 15,344 bi L (Anuário pub 2025)
- 17,211 bi L (Anuário pub 2026, método p. 7)

A queda 4,9% → 1,27% **não** se explica só pelo denominador (757 mi L / 17,2 bi ≈ 4,4%). Ou o numerador mudou, ou a tabela mudou de universo/definição. Isso tem que sair das células + nota metodológica.

Puro malte em V (29,2 → 24,7 → 29,2): documentar se o 24,7% some na revisão de vintage ou se são três medidas distintas.

Fallback: se `pdfplumber_table` estiver ilegível **nessas páginas**, avaliar camelot só então (citado em [`docs/architecture.md`](architecture.md), **não** está em `pyproject.toml`). Não instalar por via das dúvidas.

## Tarefa 4 — docs (obrigatório)

[`docs/fontes_lacunas.md`](fontes_lacunas.md):

- Ato 1, linha SIDRA: tirar “API ainda não ingestada”; anotar 11.1 vs 11.2 + implicação para a métrica.
- Ato 2, linha mix: substituir “Bloqueante” por veredito (`artefato de revisão` / `quebra metodológica` / `movimento real`) + páginas.
- Nova seção **“Verificações etapa 4”**: as três respostas, evidência, e o que **não** entra no dashboard.

Também alinhar (docs hoje estão stale):

- [`docs/etapas.md`](etapas.md) — tabela quebrada (há uma linha “Etapa atual: 4” no meio das linhas 3–4). Rodapé “Etapa atual: **1**” está errado. Depois desta etapa: **atual = 5**. Remover a linha órfã.
- [`docs/implementacao.md`](implementacao.md) — mover as três perguntas para “Feito”; incluir comandos `extract` das APIs.
- [`docs/sources.md`](sources.md) — SIDRA/BCB saem de “Ainda planejadas (API)”.
- [`docs/trabalho_futuro.md`](trabalho_futuro.md) — atualizar “Cerveja sem álcool como série própria” conforme a resposta da 8885.
- Este arquivo (`docs/etapa_4.md`): no topo, marcar **feita** quando o critério de pronto fechar (não apagar o briefing).

Opcional: uma linha na tabela de docs do [`README.md`](../README.md) apontando este briefing. Não expandir o README além disso.

**Não** alterar `docs/grain.md`.

## Fora de escopo

- Etapa 5+ (`transform/` dbt, DuckDB star schema, `qa_divergencias`)
- Dagster, GitHub Actions, Pages
- SARIMAX / `fct_cerveja_previsao`
- Power BI, demo, Zenodo
- Clima, SPA GGR, shift-share, GLP-1 como regressor (ADRs e `trabalho_futuro.md`)
- Commit/push só se o usuário pedir

## Verificação

```powershell
uv sync --extra dev
make test
make lint
uv run betscerveja extract --source sidra_8885_pim_bebidas
uv run betscerveja extract --source bcb_sgs_rendimento_real
```

Conferir que `data/01_raw/cerveja/sidra_8885_pim_bebidas/extract.parquet` tem linhas com `categoria` 11.1 e 11.2. As respostas no markdown têm página ou código de classificação, não parágrafo vago.

Se o lake local estiver vazio: `make dvc-pull` antes de inspecionar Anuários. Ingest de API só se o payload não existir (`make ingest` já cobre 8885 e SGS; 8888 e 7060 pelo CLI).

## Arquivos esperados (orientação)

Tocar no mínimo:

- `src/betscerveja/schemas/raw.py`
- `src/betscerveja/extract/runner.py`
- `tests/` (novo teste de extract API)
- `Makefile`
- `docs/fontes_lacunas.md`
- `docs/etapas.md`
- `docs/implementacao.md`
- `docs/sources.md`
- `docs/trabalho_futuro.md`
- `docs/etapa_4.md` (status)
- `docs/data_dictionary.md` só se a métrica SIDRA mudar de sentido
- `pyproject.toml` só se camelot for **necessário** após falha comprovada do pdfplumber

# Grain

Declarar a chave **antes** de escrever SQL. Na Fase 3 cada linha abaixo vira teste `unique` na chave composta e model contract do dbt.

Fatos de periodicidade maior que dia apontam para o primeiro dia do período em `dim_data` e carregam `granularidade_periodo` como atributo degenerado.

## Dimensões (`marts_core`)

| Tabela | Grain | Chave de negócio |
| --- | --- | --- |
| `dim_data` | um dia | `data` |
| `dim_geografia` | uma unidade territorial | `nivel` + `codigo` (país / macrorregião / UF) |
| `dim_fonte` | uma versão de fonte | `source_id` + `vintage_publicacao` |
| `dim_metrica` | uma métrica canônica | `metrica_id` |
| `dim_segmento_produto` | um segmento de cerveja | teor + puro_malte + estilo |
| `dim_categoria_despesa` | uma categoria de gasto doméstico | `categoria_id` |
| `dim_recorte_demografico` | uma combinação etária/sexo/classe/renda | hash dos atributos |

`dim_fonte` sem `vintage_publicacao` torna impossível representar as duas produções de 2024.

`dim_metrica` precisa separar `fluxo_bruto_apostado`, `ggr` e `destinacoes_legais`. GGR oficial da SPA está fora de escopo; no lake o fluxo oficial é o Pix do EE119.

Números esparsos de apostas (EE119, IBJR/ANJL, IEPS, Locomotiva, Klavi) entram em `fct_indicador_declarado`, não em fato "oficial" próprio.

## Fatos (`marts_core`)

| Tabela | Grain | Chave |
| --- | --- | --- |
| `fct_serie_mensal` | mês × métrica × geografia | `data_inicio`, `metrica_id`, `geografia_id` |
| `fct_indicador_declarado` | fonte × métrica × período × geografia × recorte | inclui `pagina` e `citacao_textual` |
| `fct_substituicao_declarada` | fonte × categoria de despesa × recorte | eixo do projeto |
| `fct_mercado_cerveja_anual` | ano de referência × vintage × UF | **vintage na chave** |

## Analytics

| Tabela | Grain | Alimenta |
| --- | --- | --- |
| `agg_panorama_mensal` | um mês | Ato 1 |
| `qa_divergencias` | métrica × período × par de fontes/vintages | Ato 1 |
| `agg_de_onde_saiu_o_dinheiro` | categoria × recorte | Ato 2 |
| `agg_mix_produto` | ano ref × vintage × segmento | Ato 2 |
| `agg_estrutura_setorial` | setor × métrica | Ato 3 |
| `agg_indicadores_declarados` | fonte × métrica × período | página de proveniência |

## ML (`marts_ml`)

| Tabela | Grain |
| --- | --- |
| `ml_dataset_cerveja_mensal` | um mês (alvo + features) |
| `fct_cerveja_previsao` | um mês (`realizado`, `previsto`, IC, `dentro_do_intervalo`) |
| `ml_metricas` | uma execução |
| `ml_coeficientes` | um regressor por execução |

## O que não tem grain (ainda)

Decomposição shift-share foi descartada: três pontos anuais, um deles com dois valores. Análise estrutural em nível no lugar.

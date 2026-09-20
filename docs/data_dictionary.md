# Dicionário de métricas

Catálogo vivo: [`conf/metrics.yml`](../conf/metrics.yml). Seed `seed_metricas` e dimensão `dim_metrica` no dbt. GGR e destinações legais existem no catálogo; não saem como linhas de fato.

## Apostas — três coisas diferentes

| id | O que é | Ordem de grandeza no acervo |
| --- | --- | --- |
| `fluxo_bruto_apostado` | Pix enviado às casas | ~R$ 20 bi / mês (EE119, ago/2024) |
| `ggr` | Receita líquida da operadora | Fora de escopo neste projeto (ADR 0004) |
| `destinacoes_legais` | 12% do GGR | Sem série no lake |

Usar "faturamento das bets" sem dizer qual dos três é erro.

## Cerveja

| id | Unidade | Fonte |
| --- | --- | --- |
| `producao_cerveja_litros` | litro | MAPA Anuário (anual, a partir de ref 2023) |
| `producao_bebidas_alcoolicas_indice` | índice | SIDRA 8885 mensal, categoria 11.1 (`129192`) |
| `producao_industrial_geral_indice` | índice | SIDRA 8888 mensal, indústria geral (`129314`) |
| `ipca_cerveja` | índice | SIDRA 7060, item 1114084 (no domicílio) |
| `rendimento_real` | BRL constante | BCB SGS 24364 |

`producao_bebidas_alcoolicas_indice` é índice de **estabelecimento** CNAE 11.1, não de produto. A subclasse CONCLA 1113-5/02 (sob 11.1) inclui cerveja sem álcool; a série não é “só cerveja com álcool”. Continua sendo o melhor proxy mensal de produção de cerveja no lake.

Produção MAPA ≠ consumo Euromonitor. Não somar, não interpolar, não emendar.

## Substituição

| id | Unidade | Fonte |
| --- | --- | --- |
| `substituicao_categoria_despesa` | % de respondentes | Locomotiva via Strategy& |
| `participacao_orcamento_apostas` | % da renda | mesmo relatório; Fundaj PCE em recorte PBF |
| `empregos_setor_apostas` | pessoas | IEPS (formais/RAIS) vs IBJR/ANJL (diretos e indiretos) — duas linhas, não um número |

O grain é respondente/classe, não litro de cerveja.

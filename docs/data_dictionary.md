# Dicionário de métricas

Catálogo vivo: [`conf/metrics.yml`](../conf/metrics.yml). Na Fase 3 vira seed `dim_metrica`. Até lá, esta página existe para ninguém misturar unidades.

## Apostas — três coisas diferentes

| id | O que é | Ordem de grandeza no acervo |
| --- | --- | --- |
| `fluxo_bruto_apostado` | Pix enviado às casas | ~R$ 20 bi / mês (EE119, ago/2024) |
| `ggr` | Receita líquida da operadora | ~R$ 3 bi / mês (Panorama SPA, ausente) |
| `destinacoes_legais` | 12% do GGR | uma ordem menor que o GGR |

Usar "faturamento das bets" sem dizer qual dos três é erro.

## Cerveja

| id | Unidade | Fonte |
| --- | --- | --- |
| `producao_cerveja_litros` | litro | MAPA Anuário (anual, a partir de ref 2023) |
| `producao_bebidas_alcoolicas_indice` | índice | SIDRA 8885 mensal |
| `ipca_cerveja` | índice | SIDRA 7060 |

Produção MAPA ≠ consumo Euromonitor. Não somar, não interpolar, não emendar.

## Substituição

| id | Unidade | Fonte |
| --- | --- | --- |
| `substituicao_categoria_despesa` | % de respondentes | Locomotiva via Strategy& |
| `participacao_orcamento_apostas` | % da renda | mesmo relatório; Fundaj PCE em recorte PBF |

O grain é respondente/classe, não litro de cerveja.

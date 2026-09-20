-- Ato 1. Um mês na janela 2023–2026. 8885 só via fato 11.1. Sem produção MAPA anual.

with base as (
    select
        data_inicio,
        metrica_id,
        valor
    from {{ ref("fct_serie_mensal") }}
    where
        data_inicio >= date '2023-01-01'
        and data_inicio < date '2027-01-01'
        and metrica_id in (
            'producao_bebidas_alcoolicas_indice',
            'producao_industrial_geral_indice',
            'ipca_cerveja',
            'rendimento_real'
        )
)

select
    data_inicio,
    max(case when metrica_id = 'producao_bebidas_alcoolicas_indice' then valor end)
        as producao_bebidas_alcoolicas_indice,
    max(case when metrica_id = 'producao_industrial_geral_indice' then valor end)
        as producao_industrial_geral_indice,
    max(case when metrica_id = 'ipca_cerveja' then valor end) as ipca_cerveja,
    max(case when metrica_id = 'rendimento_real' then valor end) as rendimento_real
from base
group by data_inicio

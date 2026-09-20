-- Dataset do SARIMAX (etapa 8). Um mês em que existem alvo e as duas exógenas.
-- Sem PIM geral. Sem corte em 2023: o treino usa o histórico longo.

with serie as (
    select
        data_inicio,
        metrica_id,
        valor
    from {{ ref("fct_serie_mensal") }}
    where
        geografia_id = 'pais|BR'
        and metrica_id in (
            'producao_bebidas_alcoolicas_indice',
            'ipca_cerveja',
            'rendimento_real'
        )
),

pivoted as (
    select
        data_inicio,
        max(case when metrica_id = 'producao_bebidas_alcoolicas_indice' then valor end)
            as producao_bebidas_alcoolicas_indice,
        max(case when metrica_id = 'ipca_cerveja' then valor end) as ipca_cerveja,
        max(case when metrica_id = 'rendimento_real' then valor end) as rendimento_real
    from serie
    group by data_inicio
)

select *
from pivoted
where
    producao_bebidas_alcoolicas_indice is not null
    and ipca_cerveja is not null
    and rendimento_real is not null

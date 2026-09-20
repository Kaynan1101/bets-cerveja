-- SIDRA YYYYMM -> primeiro dia do mês; BCB SGS já vem como DD/MM/YYYY do ponto.
-- 8885: só 11.1 (129192). 7060: item cerveja 1114084 (categoria_id 7396 no extract local).
-- Histórico completo no fato; a janela 2023-2026 é filtro analítico, não corte do raw.

with api as (
    select * from {{ ref("stg_raw_api") }}
),

sidra_8885 as (
    select
        make_date(
            try_cast(substr(periodo, 1, 4) as integer),
            try_cast(substr(periodo, 5, 2) as integer),
            1
        ) as data_inicio,
        'producao_bebidas_alcoolicas_indice' as metrica_id,
        source_id,
        0 as vintage_publicacao,
        'pais|BR' as geografia_id,
        valor,
        'indice' as unidade,
        'mes' as granularidade_periodo
    from api
    where
        source_id = 'sidra_8885_pim_bebidas'
        and categoria_id = '129192'
        and valor is not null
),

sidra_8888 as (
    select
        make_date(
            try_cast(substr(periodo, 1, 4) as integer),
            try_cast(substr(periodo, 5, 2) as integer),
            1
        ) as data_inicio,
        'producao_industrial_geral_indice' as metrica_id,
        source_id,
        0 as vintage_publicacao,
        'pais|BR' as geografia_id,
        valor,
        'indice' as unidade,
        'mes' as granularidade_periodo
    from api
    where
        source_id = 'sidra_8888_pim_geral'
        and (categoria_id = '129314' or categoria_id is null)
        and valor is not null
),

sidra_7060 as (
    select
        make_date(
            try_cast(substr(periodo, 1, 4) as integer),
            try_cast(substr(periodo, 5, 2) as integer),
            1
        ) as data_inicio,
        'ipca_cerveja' as metrica_id,
        source_id,
        0 as vintage_publicacao,
        'pais|BR' as geografia_id,
        valor,
        'indice' as unidade,
        'mes' as granularidade_periodo
    from api
    where
        source_id = 'sidra_7060_ipca'
        and classificacao_id = '315'
        and (
            categoria_id = '7396'
            or lower(categoria_nome) like '%1114084.cerveja%'
        )
        and valor is not null
),

bcb_sgs as (
    select
        try_strptime(periodo, '%d/%m/%Y')::date as data_inicio,
        'rendimento_real' as metrica_id,
        source_id,
        0 as vintage_publicacao,
        'pais|BR' as geografia_id,
        valor,
        'brl_constante' as unidade,
        'mes' as granularidade_periodo
    from api
    where
        source_id = 'bcb_sgs_rendimento_real'
        and valor is not null
        and try_strptime(periodo, '%d/%m/%Y') is not null
)

select * from sidra_8885
union all
select * from sidra_8888
union all
select * from sidra_7060
union all
select * from bcb_sgs

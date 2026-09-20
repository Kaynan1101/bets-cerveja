-- Métrica × período × par de fontes/vintages. Pares que já estão nos fatos
-- saem de SQL; o restante vem de seed_qa_divergencias (citação no lake).

with producao_2024 as (
    select
        metrica_id,
        ano_referencia,
        data_inicio,
        source_id,
        vintage_publicacao,
        valor,
        unidade
    from {{ ref("fct_mercado_cerveja_anual") }}
    where
        metrica_id = 'producao_cerveja_litros'
        and ano_referencia = 2024
),

par_producao as (
    select
        a.metrica_id,
        a.ano_referencia,
        a.data_inicio,
        a.source_id as source_id_a,
        a.vintage_publicacao as vintage_a,
        a.valor as valor_a,
        a.unidade as unidade_a,
        b.source_id as source_id_b,
        b.vintage_publicacao as vintage_b,
        b.valor as valor_b,
        b.unidade as unidade_b,
        'vintage' as tipo_divergencia,
        'Produção 2024 original (pub 2025 p. 51) vs retificada (pub 2026 p. 51). Sinal da variação de 2025 depende do vintage.' as nota
    from producao_2024 as a
    inner join producao_2024 as b
        on a.vintage_publicacao < b.vintage_publicacao
),

emprego as (
    select
        metrica_id,
        source_id,
        vintage_publicacao,
        data_inicio,
        valor,
        unidade
    from {{ ref("fct_indicador_declarado") }}
    where metrica_id = 'empregos_setor_apostas'
),

par_emprego as (
    select
        a.metrica_id,
        2025 as ano_referencia,
        make_date(2025, 1, 1) as data_inicio,
        a.source_id as source_id_a,
        a.vintage_publicacao as vintage_a,
        a.valor as valor_a,
        a.unidade as unidade_a,
        b.source_id as source_id_b,
        b.vintage_publicacao as vintage_b,
        b.valor as valor_b,
        b.unidade as unidade_b,
        'definicao' as tipo_divergencia,
        'IEPS 1.144 empregos formais (31/12/2024, p. 31) vs IBJR/ANJL 15,5 mil diretos e indiretos (nov/2025, p. 3). Duas definições, não um número.' as nota
    from emprego as a
    inner join emprego as b
        on
            a.source_id = 'ieps_dossie_bets_saude'
            and b.source_id = 'lca_ibjr_anjl_panorama_apostas_2025'
),

seed as (
    select
        metrica_id,
        try_cast(ano_referencia as integer) as ano_referencia,
        try_cast(data_inicio as date) as data_inicio,
        source_id_a,
        try_cast(vintage_a as integer) as vintage_a,
        try_cast(valor_a as double) as valor_a,
        unidade_a,
        source_id_b,
        try_cast(vintage_b as integer) as vintage_b,
        try_cast(valor_b as double) as valor_b,
        unidade_b,
        tipo_divergencia,
        nota
    from {{ ref("seed_qa_divergencias") }}
)

select * from par_producao
union all
select * from par_emprego
union all
select * from seed

-- Produção nacional em litros. Preferir número extraído do trecho nas páginas
-- citadas; celulas_json dessas páginas não tem o total nacional (só regiões).
-- Fallback: seed_citacoes (mesma página e valor).

with textos as (
    select
        source_id,
        pagina,
        trecho
    from {{ ref("stg_raw_pdf") }}
    where metodo = 'pdfplumber_text'
),

extraido as (
    select
        'anuario_cerveja_ref2023_pub2024' as source_id,
        2024 as vintage_publicacao,
        2023 as ano_referencia,
        44 as pagina,
        {{ parse_br_number("regexp_extract(trecho, '15\\.361\\.344\\.112,77')") }} as valor
    from textos
    where source_id = 'anuario_cerveja_ref2023_pub2024' and pagina = 44

    union all

    select
        'anuario_cerveja_ref2024_pub2025' as source_id,
        2025 as vintage_publicacao,
        2024 as ano_referencia,
        51 as pagina,
        {{ parse_br_number("regexp_extract(trecho, '15\\.344\\.065\\.267,36')") }} as valor
    from textos
    where source_id = 'anuario_cerveja_ref2024_pub2025' and pagina = 51

    union all

    select
        'anuario_cerveja_ref2025_pub2026' as source_id,
        2026 as vintage_publicacao,
        2024 as ano_referencia,
        51 as pagina,
        {{ parse_br_number("regexp_extract(trecho, '17\\.210\\.754\\.610,75')") }} as valor
    from textos
    where source_id = 'anuario_cerveja_ref2025_pub2026' and pagina = 51

    union all

    select
        'anuario_cerveja_ref2025_pub2026' as source_id,
        2026 as vintage_publicacao,
        2025 as ano_referencia,
        51 as pagina,
        {{ parse_br_number("regexp_extract(trecho, '15\\.688\\.083\\.191,69')") }} as valor
    from textos
    where source_id = 'anuario_cerveja_ref2025_pub2026' and pagina = 51
),

seed_fallback as (
    select
        source_id,
        vintage_publicacao,
        ano_referencia,
        pagina,
        try_cast(valor as double) as valor,
        citacao_textual
    from {{ ref("seed_citacoes") }}
    where fato = 'mercado_anual'
)

select
    seed_fallback.source_id,
    seed_fallback.vintage_publicacao,
    seed_fallback.ano_referencia,
    seed_fallback.pagina,
    coalesce(extraido.valor, seed_fallback.valor) as valor,
    'litro' as unidade,
    'producao_cerveja_litros' as metrica_id,
    'pais|BR' as geografia_id,
    make_date(seed_fallback.ano_referencia, 1, 1) as data_inicio,
    'ano' as granularidade_periodo,
    seed_fallback.citacao_textual
from seed_fallback
left join extraido
    on
        seed_fallback.source_id = extraido.source_id
        and seed_fallback.ano_referencia = extraido.ano_referencia
        and seed_fallback.vintage_publicacao = extraido.vintage_publicacao

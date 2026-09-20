select
    {{ recorte_id("null", "null", "null") }} as recorte_id,
    cast(null as varchar) as classe,
    cast(null as varchar) as programa,
    cast(null as varchar) as amostra,
    'Brasil / sem recorte' as descricao

union all

select
    {{ recorte_id("'C/D/E'", "null", "null") }},
    'C/D/E',
    cast(null as varchar),
    cast(null as varchar),
    'Classes C/D/E (Locomotiva)'

union all

select
    {{ recorte_id("'D/E'", "null", "null") }},
    'D/E',
    cast(null as varchar),
    cast(null as varchar),
    'Classes D/E (Locomotiva / POF)'

union all

select
    {{ recorte_id("null", "'PBF'", "null") }},
    cast(null as varchar),
    'PBF',
    cast(null as varchar),
    'Beneficiários do Bolsa Família'

union all

select
    {{ recorte_id("null", "'PBF'", "'mediana_r100'") }},
    cast(null as varchar),
    'PBF',
    'mediana_r100',
    'Bolsa Família após mediana de R$ 100 em apostas (Fundaj NT39)'

union all

select
    {{ recorte_id("null", "null", "'open_finance'") }},
    cast(null as varchar),
    cast(null as varchar),
    'open_finance',
    'Amostra Open Finance (Klavi), não censo'

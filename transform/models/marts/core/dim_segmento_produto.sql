-- Dimensão de apoio. Mix sem álcool / puro malte não entra como tendência no fato.

select
    'qualquer|qualquer|qualquer' as segmento_id,
    'qualquer' as teor,
    'qualquer' as puro_malte,
    'qualquer' as estilo

union all

select
    'com_alcool|nao|lager',
    'com_alcool',
    'nao',
    'lager'

union all

select
    'sem_alcool|nao|qualquer',
    'sem_alcool',
    'nao',
    'qualquer'

union all

select
    'com_alcool|sim|puro_malte',
    'com_alcool',
    'sim',
    'puro_malte'

select
    source_id::varchar as source_id,
    metodo::varchar as metodo,
    periodo::varchar as periodo,
    localidade_id::varchar as localidade_id,
    localidade_nome::varchar as localidade_nome,
    variavel_id::varchar as variavel_id,
    variavel_nome::varchar as variavel_nome,
    classificacao_id::varchar as classificacao_id,
    classificacao_nome::varchar as classificacao_nome,
    categoria_id::varchar as categoria_id,
    categoria_nome::varchar as categoria_nome,
    try_cast(valor as double) as valor,
    unidade::varchar as unidade
from {{ source("raw", "sidra_8885_pim_bebidas") }}

union all

select
    source_id::varchar as source_id,
    metodo::varchar as metodo,
    periodo::varchar as periodo,
    localidade_id::varchar as localidade_id,
    localidade_nome::varchar as localidade_nome,
    variavel_id::varchar as variavel_id,
    variavel_nome::varchar as variavel_nome,
    classificacao_id::varchar as classificacao_id,
    classificacao_nome::varchar as classificacao_nome,
    categoria_id::varchar as categoria_id,
    categoria_nome::varchar as categoria_nome,
    try_cast(valor as double) as valor,
    unidade::varchar as unidade
from {{ source("raw", "sidra_8888_pim_geral") }}

union all

select
    source_id::varchar as source_id,
    metodo::varchar as metodo,
    periodo::varchar as periodo,
    localidade_id::varchar as localidade_id,
    localidade_nome::varchar as localidade_nome,
    variavel_id::varchar as variavel_id,
    variavel_nome::varchar as variavel_nome,
    classificacao_id::varchar as classificacao_id,
    classificacao_nome::varchar as classificacao_nome,
    categoria_id::varchar as categoria_id,
    categoria_nome::varchar as categoria_nome,
    try_cast(valor as double) as valor,
    unidade::varchar as unidade
from {{ source("raw", "sidra_7060_ipca") }}

union all

select
    source_id::varchar as source_id,
    metodo::varchar as metodo,
    periodo::varchar as periodo,
    localidade_id::varchar as localidade_id,
    localidade_nome::varchar as localidade_nome,
    variavel_id::varchar as variavel_id,
    variavel_nome::varchar as variavel_nome,
    classificacao_id::varchar as classificacao_id,
    classificacao_nome::varchar as classificacao_nome,
    categoria_id::varchar as categoria_id,
    categoria_nome::varchar as categoria_nome,
    try_cast(valor as double) as valor,
    unidade::varchar as unidade
from {{ source("raw", "bcb_sgs_rendimento_real") }}

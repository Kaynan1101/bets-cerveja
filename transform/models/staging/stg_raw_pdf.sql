select
    source_id::varchar as source_id,
    metodo::varchar as metodo,
    try_cast(pagina as integer) as pagina,
    trecho::varchar as trecho,
    try_cast(tabela_idx as integer) as tabela_idx,
    celulas_json::varchar as celulas_json
from {{ source("raw", "anuario_cerveja_ref2023_pub2024") }}

union all

select
    source_id::varchar as source_id,
    metodo::varchar as metodo,
    try_cast(pagina as integer) as pagina,
    trecho::varchar as trecho,
    try_cast(tabela_idx as integer) as tabela_idx,
    celulas_json::varchar as celulas_json
from {{ source("raw", "anuario_cerveja_ref2024_pub2025") }}

union all

select
    source_id::varchar as source_id,
    metodo::varchar as metodo,
    try_cast(pagina as integer) as pagina,
    trecho::varchar as trecho,
    try_cast(tabela_idx as integer) as tabela_idx,
    celulas_json::varchar as celulas_json
from {{ source("raw", "anuario_cerveja_ref2025_pub2026") }}

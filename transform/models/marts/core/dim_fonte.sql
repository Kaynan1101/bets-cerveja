select
    source_id,
    vintage_publicacao,
    source_id || '|' || vintage_publicacao::varchar as fonte_id,
    tier_confiabilidade,
    lower(e_oficial::varchar) in ('true', '1', 't') as e_oficial,
    try_cast(nullif(ano_referencia::varchar, '') as integer) as ano_referencia,
    titulo,
    dominio,
    status_acervo
from {{ ref("seed_fontes") }}

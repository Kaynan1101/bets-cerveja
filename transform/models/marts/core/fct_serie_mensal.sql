select
    data_inicio,
    metrica_id,
    geografia_id,
    source_id,
    vintage_publicacao,
    valor,
    unidade,
    granularidade_periodo
from {{ ref("int_serie_mensal") }}
where data_inicio is not null

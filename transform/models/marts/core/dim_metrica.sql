select
    metrica_id,
    unidade,
    periodicidade,
    descricao
from {{ ref("seed_metricas") }}

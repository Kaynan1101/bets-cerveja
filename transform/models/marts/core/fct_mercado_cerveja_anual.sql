select
    ano_referencia,
    vintage_publicacao,
    geografia_id,
    source_id,
    metrica_id,
    data_inicio,
    valor,
    unidade,
    pagina,
    citacao_textual,
    granularidade_periodo
from {{ ref("int_producao_anuario") }}

select
    source_id,
    vintage_publicacao,
    categoria_despesa_id as categoria_id,
    recorte_id,
    metrica_id,
    geografia_id,
    coalesce(data_inicio, make_date(ano_referencia, 1, 1)) as data_inicio,
    valor,
    unidade,
    pagina,
    citacao_textual
from {{ ref("int_citacoes") }}
where fato = 'substituicao'

select
    source_id,
    vintage_publicacao,
    metrica_id,
    coalesce(data_inicio, make_date(ano_referencia, 1, 1)) as data_inicio,
    geografia_id,
    recorte_id,
    pagina,
    citacao_textual,
    valor,
    unidade,
    case
        when data_inicio is not null then 'mes'
        else 'ano'
    end as granularidade_periodo
from {{ ref("int_citacoes") }}
where fato = 'indicador'

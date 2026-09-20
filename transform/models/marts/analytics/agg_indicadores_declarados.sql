-- Página de proveniência de fct_indicador_declarado. Sem GGR / destinações legais.

select
    source_id,
    vintage_publicacao,
    metrica_id,
    data_inicio,
    geografia_id,
    recorte_id,
    pagina,
    citacao_textual,
    valor,
    unidade,
    granularidade_periodo
from {{ ref("fct_indicador_declarado") }}
where metrica_id not in ('ggr', 'destinacoes_legais')

select
    source_id,
    metrica_id,
    vintage_publicacao,
    ano_referencia,
    try_cast(periodo as date) as data_inicio,
    try_cast(valor as double) as valor,
    unidade,
    try_cast(pagina as integer) as pagina,
    citacao_textual,
    geografia_nivel,
    geografia_codigo,
    recorte_classe,
    recorte_programa,
    recorte_amostra,
    categoria_despesa_id,
    fato,
    {{ recorte_id("nullif(recorte_classe, '')", "nullif(recorte_programa, '')", "nullif(recorte_amostra, '')") }}
        as recorte_id,
    geografia_nivel || '|' || geografia_codigo as geografia_id
from {{ ref("seed_citacoes") }}

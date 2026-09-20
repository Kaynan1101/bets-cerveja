-- Ato 2. Categoria × recorte. Locomotiva p. 19, inclusive 48% bares/restaurantes/delivery.

select
    categoria_id,
    recorte_id,
    source_id,
    vintage_publicacao,
    metrica_id,
    geografia_id,
    data_inicio,
    valor,
    unidade,
    pagina,
    citacao_textual
from {{ ref("fct_substituicao_declarada") }}

-- Ato 3. Setor × métrica. Emprego apostas em duas definições. Sem GGR.
-- Emprego cerveja só com citação no Anuário (CAGED CNAE 1113-5/02).

select
    case
        when source_id = 'ieps_dossie_bets_saude' then 'apostas_formais'
        when source_id = 'lca_ibjr_anjl_panorama_apostas_2025' then 'apostas_diretos_indiretos'
        when metrica_id = 'empregos_setor_cerveja' then 'cerveja_fabricacao'
    end as setor,
    metrica_id,
    source_id,
    vintage_publicacao,
    data_inicio,
    valor,
    unidade,
    pagina,
    citacao_textual
from {{ ref("fct_indicador_declarado") }}
where
    metrica_id in ('empregos_setor_apostas', 'empregos_setor_cerveja')
    and metrica_id not in ('ggr', 'destinacoes_legais')

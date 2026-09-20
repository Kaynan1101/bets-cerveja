-- Ato 2. Estrutura ano × vintage × segmento. Sem sparkline de mix sem álcool
-- nem V de puro malte (quebra metodológica / três vintages). Vazio de propósito.

select
    cast(null as integer) as ano_referencia,
    cast(null as integer) as vintage_publicacao,
    cast(null as varchar) as segmento_id,
    cast(null as varchar) as source_id,
    cast(null as varchar) as metrica_id,
    cast(null as double) as valor,
    cast(null as varchar) as unidade,
    cast(null as boolean) as usar_como_tendencia,
    cast(null as varchar) as nota
where false

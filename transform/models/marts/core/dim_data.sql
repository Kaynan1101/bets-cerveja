-- Spine de datas em SQL DuckDB (sem dbt_utils). Cobre o histórico SIDRA até 2026-12-31.

select
    calendar_day::date as data,
    extract(year from calendar_day)::integer as ano,
    extract(month from calendar_day)::integer as mes,
    extract(quarter from calendar_day)::integer as trimestre,
    extract(dow from calendar_day)::integer as dia_semana,
    make_date(
        extract(year from calendar_day)::integer,
        extract(month from calendar_day)::integer,
        1
    ) as data_inicio_mes,
    make_date(extract(year from calendar_day)::integer, 1, 1) as data_inicio_ano
from generate_series(date '2002-01-01', date '2026-12-31', interval '1 day') as t(calendar_day)

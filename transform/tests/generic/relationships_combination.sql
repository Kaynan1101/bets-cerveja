{% test relationships_combination(model, combination_of_columns, to, to_columns) %}
{# FK composta sem dbt_utils. Nulos no filho são ignorados, como no relationships nativo. #}
select
    {% for col in combination_of_columns %}
    child.{{ col }}{% if not loop.last %},{% endif %}
    {% endfor %}
from {{ model }} as child
where
    {% for col in combination_of_columns %}
    child.{{ col }} is not null{% if not loop.last %} and {% endif %}
    {% endfor %}
    and not exists (
        select 1
        from {{ to }} as parent
        where
            {% for i in range(combination_of_columns | length) %}
            parent.{{ to_columns[i] }} = child.{{ combination_of_columns[i] }}
            {% if not loop.last %} and {% endif %}
            {% endfor %}
    )
{% endtest %}

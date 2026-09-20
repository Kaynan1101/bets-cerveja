{% macro parse_br_number(expr) %}
try_cast(replace(replace({{ expr }}, '.', ''), ',', '.') as double)
{% endmacro %}

{% macro recorte_id(classe, programa, amostra) %}
lower(md5(concat_ws('|', coalesce({{ classe }}, ''), coalesce({{ programa }}, ''), coalesce({{ amostra }}, ''))))
{% endmacro %}

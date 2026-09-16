# Como adicionar uma fonte

O contrato do projeto é: **fonte nova entra no YAML antes de entrar no lake**.

1. Coloque uma entrada em [`conf/sources.yml`](conf/sources.yml) com `id` slug, `ano_referencia` e `vintage_publicacao` separados, `tier_confiabilidade`, `e_oficial` e `conflito_de_interesse` se houver.
2. Rode `uv run betscerveja sources validate`. Se o Pydantic recusar, o YAML está errado — não force o arquivo para o lake.
3. Atualize a matriz em [`docs/fontes_lacunas.md`](docs/fontes_lacunas.md): que afirmação essa fonte sustenta, em que granularidade, e o que continua faltando.
4. Se a fonte for PDF ou HTML já baixado, grave em `data/00_landing/<id>/seed/` com o `landing_filename` declarado. Não grave pastas `*_files` de páginas salvas no Chrome.
5. Só na Fase 1 o adapter (`http_file`, `http_page`, `api_sidra`, `api_bcb`) passa a baixar sozinho. Até lá, coleta é manual e o `status_acervo` fica `pendente` ou `no_lake`.

Não copie número de matéria jornalística para o mart sem registrar a fonte primária citada (Euromonitor, Nielsen, Klavi, Scanntech). O HTML entra como evidência de que o número circulou; a métrica canônica aponta para quem mediu.

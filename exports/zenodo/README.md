# bets-cerveja — dataset derivado

Pacote para o Zenodo. Só dado **derivado**: Parquet dos marts,
PNG das figuras e atribuição. Não inclui DuckDB, `.env`, lake DVC
nem bytes de `data/00_landing`.

DOI (placeholder até reservar o recorde): https://doi.org/10.5281/zenodo.XXXX

Código: https://github.com/Kaynan1101/bets-cerveja (MIT). Dados derivados: [LICENSE-DATA](LICENSE-DATA)
(CC BY 4.0).

## O que é cada arquivo

- `marts/agg_panorama_mensal.parquet` — Ato 1, SIDRA 8885 11.1
  (PIM geral / IPCA só como contexto)
- `marts/fct_mercado_cerveja_anual.parquet` — produção anual MAPA
  (2024 em dois vintages, sem média)
- `marts/fct_cerveja_previsao.parquet` — contrafactual SARIMAX
  (realizado, previsto, IC 95%)
- `marts/agg_de_onde_saiu_o_dinheiro.parquet` — Ato 2, Locomotiva p. 19
- `marts/agg_estrutura_setorial.parquet` — Ato 3, IEPS vs IBJR (sem média)
- `marts/qa_divergencias.parquet` — divergências rotuladas
- `marts/agg_indicadores_declarados.parquet` — proveniência / citações
- `marts/ml_metricas.parquet` — uma linha por execução SARIMAX
- `marts/ml_coeficientes.parquet` — coeficientes, erro padrão, p-valor, IC
- `figures/*.png` + `figures/index.html` — os cinco gráficos e o índice
- `LICENSE-DATA` — CC BY 4.0 dos derivados
- `CITATION.cff` / `.zenodo.json` — metadados (DOI placeholder)
- `MANIFEST.txt` — lista dos arquivos deste pacote

## Como ler a ponte Locomotiva

48% dos apostadores das classes C/D/E dizem ter tirado dinheiro de
bares, restaurantes e delivery. Isso é **survey**, não substituição
litro a litro de cerveja. Nenhuma fonte do acervo liga, de forma
quantificada, redução de consumo de cerveja a aumento de gasto com
apostas.

Mix de produto (cerveja sem álcool 4,9%→1,27% e o V de puro malte)
**não entra no gráfico**. Ver `qa_divergencias` e a documentação do
repositório.

## Atribuição das fontes primárias

- MAPA — Anuário da Cerveja (produção anual, emprego na fabricação)
- IBGE — SIDRA 8885 (PIM bebidas), 8888 (PIM geral), 7060 (IPCA cerveja)
- BCB — SGS 24364 (rendimento real); Estudo Especial 119 (fluxo Pix)
- Instituto Locomotiva / Strategy& — survey de substituição (p. 19)
- IEPS — empregos formais no setor de apostas
- IBJR / ANJL / LCA — panorama de apostas (diretos e indiretos;
  conflito de interesse)
- Demais citações em `agg_indicadores_declarados` e `qa_divergencias`

Os bytes originais (PDF/HTML/JSON de `data/00_landing`) continuam sob
a licença de cada publicador. Este pacote não os republica.

## O que isto não é

Não é GGR da SPA. Não é evidência causal de que as bets “pegaram”
litros de cerveja. O contrafactual SARIMAX descreve ausência de
anomalia agregada na série SIDRA 8885 11.1.

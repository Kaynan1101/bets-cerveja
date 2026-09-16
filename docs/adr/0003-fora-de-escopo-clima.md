# ADR 0003 — Clima fora de escopo

- Status: aceito
- Data: 2026-09-15

## Contexto

Temperatura e safra de cevada/lúpulo explicam parte da sazonalidade da cerveja, mas não respondem de onde saiu o dinheiro das apostas. Incluí-los abre um projeto de clima agrícola.

## Decisão

Não ingestir série climática nem de insumos. Regressores do SARIMAX: renda real e IPCA de cerveja. GLP-1 não entra como variável; só como hipótese rival no texto.

## Consequências

- Modelo mais pobre em confundidores sazonais.
- Narrativa alinhada ao eixo do portfólio.

## Alternativas rejeitadas

- INMET / NOAA como dim extra. Trabalho futuro se a pergunta mudar.

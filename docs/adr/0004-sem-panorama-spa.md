# ADR 0004 — Sem Panorama da SPA

- Status: aceito
- Data: 2026-09-15

## Contexto

A Secretaria de Prêmios e Apostas publica o panorama oficial de GGR, apostadores e destinações legais. Esse PDF não está no acervo. Esperá-lo bloqueava extração e o Ato 3.

## Decisão

Trabalhar só com o que já está no lake. `spa_panorama_apostas_2025` fica `fora_de_escopo`. Não há `fct_apostas_oficial`.

Substitutos:

- fluxo Pix: BCB EE119
- emprego/capital/tributos: LCA+Cruz / IBJR / ANJL (tier C) e IEPS
- substituição de orçamento: Locomotiva via Strategy&
- apostadores em amostra: Klavi

## Consequências

O dashboard não mostra GGR oficial nem destinações de 12%. O artigo declara a lacuna. Emprego setorial entra como divergência IEPS vs IBJR, não como número único.

## Alternativas rejeitadas

Esperar o PDF da SPA. Atrasava o pipeline sem mudar o eixo (substituição de orçamento).

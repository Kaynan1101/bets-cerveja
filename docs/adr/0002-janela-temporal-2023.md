# ADR 0002 — Janela analítica 2023–2026

- Status: aceito
- Data: 2026-09-15

## Contexto

A premissa inicial (queda de consumo de cerveja 2021–2025) não sobrevive aos Anuários. MAPA só publica volume de produção a partir do ano de referência 2023. Apostas oficiais existem de fato a partir da Lei 14.790 (dez/2023).

## Decisão

A análise e os marts cobrem 2023–2026. Anuários 2021–2022 e matérias de 2021–2022 ficam no lake como contexto e para divergência metodológica (kg vs litros), não como série do Ato 1.

## Consequências

- Não emendar Euromonitor (consumo de varejo, fonte paga) com MAPA (produção declarada).
- Shift-share inviável (três pontos). Análise estrutural em nível no lugar.
- SARIMAX ainda treina no histórico longo da SIDRA e projeta a janela.

## Alternativas rejeitadas

- Janela 2021–2025: fato de bets quase vazio, produção MAPA inexistente, quebra kg→L no comércio exterior.

# Trabalho futuro

Fora do escopo atual de propósito. Não implementar nestas fases.

## Clima e safra de insumos

Descartado. Abre um leque que não responde "de onde saiu o dinheiro".

## Shift-share da composição de cerveja

Três pontos anuais (2023–2025), um deles com dois valores. Decomposição não se sustenta. Se o MAPA publicar mais dois Anuários com metodologia estável, revisitar.

## Teste distribucional microdado a microdado

Klavi e Fundaj sugerem o mecanismo (cortar varejo, contas, saúde). Não temos painel de cartão cruzando cerveja e bets na mesma família. Sem POF nova ou microdado Open Finance acessível, não há teste.

## GLP-1 como regressor

Fica como hipótese rival no artigo (Scanntech, via jornalismo). Entrar no SARIMAX exigiria série mensal de penetração de GLP-1, que não está no lake.

## Cerveja sem álcool como série própria no contrafactual

A SIDRA 8885 **não** separa zero álcool. Categoria `129192` (11.1) é CNAE de estabelecimento; a CONCLA 1113-5/02 (sob 11.1) inclui explicitamente cerveja sem álcool. Segundo modelo no SARIMAX continua **fora de escopo**.

## Panorama da SPA

Fora de escopo. Ver [ADR 0004](adr/0004-sem-panorama-spa.md).

Fase 8. Zenodo é conta externa; não criar até o dataset derivado existir.

## Dagster vs Airflow "para o currículo"

A decisão está no [ADR 0001](adr/0001-orquestracao-dagster-em-vez-de-airflow.md). Não instalar os dois.

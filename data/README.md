# Camadas de dados

Landing é byte a byte idêntico à fonte. Nada de limpar, renomear colunas ou converter unidade aqui.

```
data/
  00_landing/   bytes originais + _manifest.jsonl (DVC, Fase 1)
  01_raw/       Parquet 1:1 com a extração, sem limpeza de negócio (DVC)
  sample/       fatia pequena commitada no Git, para demo
```

## Regras

1. **Não edite arquivos em `00_landing`.** Se o parser melhorou, reextraia para `01_raw`. Se a fonte publicou errata, grave um *novo* arquivo com outro `vintage_publicacao`.
2. O nome do Anuário da Cerveja no lake é `anuario_cerveja_refAAAA_pubBBBB.pdf`. O ano no site do MAPA é o de referência, não o de publicação. `anuario-da-cerveja-2025.pdf` era o Anuário 2026 (dados de 2025).
3. Pastas `*_files` de HTML salvo no navegador não entram no lake. São assets de página, não dado.
4. `data/00_landing` e `data/01_raw` estão no `.gitignore` até o DVC remoto existir. Não dê `git add data/00_landing`.

## Layout por fonte

```
data/00_landing/<source_id>/seed/<landing_filename>
```

`seed` marca coleta anterior ao pipeline. A ingestão da Fase 1 grava `data/00_landing/<source_id>/<YYYY-MM-DD>/`.

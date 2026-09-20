# bets-cerveja

Onde foi parar o fim de semana do brasileiro — de onde saiu o dinheiro das apostas (2023–2026).

Pipeline de dados e análise sobre a composição do gasto discricionário no Brasil depois da regulamentação das apostas. A pergunta não é se a produção de cerveja caiu no agregado (os Anuários do MAPA mostram estabilidade). A pergunta é de onde saiu o dinheiro que foi para as bets, e o que isso implica para o canal on-premise (bares, restaurantes e delivery).

## Limites causais (leia isto primeiro)

Nenhuma fonte do acervo liga, de forma quantificada, redução de consumo de cerveja a aumento de gasto com apostas. A ponte empírica é o canal **bares, restaurantes e delivery** no survey da Locomotiva (48% dos apostadores das classes C/D/E dizem ter tirado o dinheiro daí). O projeto trata isso como ponte, não como evidência de substituição litro a litro.

O contrafactual SARIMAX (Fase 6) deve confirmar **ausência de anomalia agregada**. Isso é resultado, não falha.

## Janela e stack

- Janela analítica: 2023–2026.
- Fora de escopo: clima, safra de insumos. GLP-1 entra só como hipótese rival no artigo.
- Python 3.12 (`uv`), DuckDB, dbt, DVC (Cloudflare R2), Dagster na Fase 5, Power BI na Fase 7.

## Quickstart

```powershell
uv sync --extra dev
make sources
make test
```

O acervo original (PDFs e HTMLs) vive em `data/00_landing/`, versionado por DVC no Cloudflare R2. Depois de clonar: `uv sync --extra dev` e `make dvc-pull`. Veja [docs/implementacao.md](docs/implementacao.md).

## Documentação de implementação

| Arquivo | Para quê |
| --- | --- |
| [docs/etapas.md](docs/etapas.md) | Ordem das 10 etapas até o fim |
| [docs/etapa_4.md](docs/etapa_4.md) | Briefing da etapa 4 (pedir build a um agente novo) |
| [docs/etapa_5.md](docs/etapa_5.md) | Briefing da etapa 5 (dbt + DuckDB) |
| [docs/architecture.md](docs/architecture.md) | Camadas e por que cada ferramenta está onde está |
| [docs/grain.md](docs/grain.md) | Chave de cada tabela final — escrever **antes** de modelar |
| [docs/fontes_lacunas.md](docs/fontes_lacunas.md) | Matriz afirmação → fonte. Afirmação sem fonte muda no papel |
| [docs/sources.md](docs/sources.md) | Como ler `conf/sources.yml` |
| [docs/data_dictionary.md](docs/data_dictionary.md) | Métricas canônicas (não misturar GGR com fluxo bruto) |
| [docs/trabalho_futuro.md](docs/trabalho_futuro.md) | O que ficou de fora de propósito |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Como adicionar uma fonte nova |
| [data/README.md](data/README.md) | Imutabilidade do landing |

## Licenças

Código: MIT. Dados derivados: [LICENSE-DATA](LICENSE-DATA) (CC BY 4.0, com atribuição das fontes primárias). Bytes originais continuam sob a licença de cada publicador.

# Matriz fonte → afirmação

Regra: afirmação sem fonte primária na granularidade necessária **muda no papel**, não entra no dashboard.

Janela analítica: 2023–2026. Fontes anteriores ficam no lake só como contexto e para `qa_divergencias`.

## Ato 1 — a cerveja não caiu, e a manchete depende do vintage

| Afirmação | Fonte primária | Grain disponível | Lacuna |
| --- | --- | --- | --- |
| Produção 2023 = 15.361.344.112,77 L | MAPA Anuário ref 2023 / pub 2024 | Brasil, anual | — |
| Produção 2024 = 15.344.065.267,36 L | MAPA Anuário ref 2024 / pub 2025, p. 49 | Brasil, anual | Mesma métrica, outro vintage abaixo |
| Produção 2024 retificada = 17.210.754.610,75 L | MAPA Anuário ref 2025 / pub 2026, p. 51 | Brasil, anual | Método na p. 7 (retificações voluntárias / auditoria) |
| Produção 2025 = 15.688.083.191,69 L (−8,85% vs 2024 retificado; +2,3% vs 2024 original) | MAPA Anuário ref 2025 / pub 2026 | Brasil, anual | Sinal da variação depende do vintage |
| Per capita ~70–71 L/hab; ranking mundial 22º→21º | Anuários MAPA (tabelas internacionais) | país-ano | Conferir página na extração |
| Série mensal de bebidas alcoólicas estável o bastante para o contrafactual cair no IC | SIDRA 8885, classificação 542, categoria **11.1** (`129192`) | Brasil, mensal, índice de estabelecimento CNAE | Cerveja zero **entra em 11.1**, não em 11.2 (`129193`). A métrica `producao_bebidas_alcoolicas_indice` é PIM-PF de fabricação de bebidas alcoólicas (inclui zero das cervejarias), não “só cerveja com álcool”. Sem série própria de zero. |

## Ato 2 — de onde saiu o dinheiro

| Afirmação | Fonte primária | Grain disponível | Lacuna |
| --- | --- | --- | --- |
| 52% poupança; 48% bares/restaurantes/delivery; 43% roupas; 41% cultura | Strategy& / Locomotiva, p. 19 | survey classes C/D/E, um corte | **Não é cerveja.** Ponte on-premise. Amostra de survey, tier C |
| Apostas 0,73% → 1,38% do orçamento nas classes D/E; +419% desde 2018 | mesmo relatório | classe, anual até 2023/24 | Série para antes da janela; usar como nível, não como tendência 2023–26 |
| Razão apostas/alimentação 1,5%→4,9%; apostas/lazer 10%→36% | mesmo relatório | nacional, dois pontos | — |
| Mediana R$ 100 ≡ 16,7% do Bolsa Família; PCE 1,0→0,83 | Fundaj NT39 | PBF, recorte nacional | — |
| 5 mi beneficiários PBF, R$ 3 bi em ago/2024, 70% chefes de família | BCB EE119 | mês, PBF | Um mês só. Não é série |
| 3,7 mi apostadores Klavi em 2025 (dobro de 2024); 18% alto risco | Klavi (HTML próprio + Valor Investe) | amostra Open Finance | Não é censo. Não tratar como total nacional |
| Mix sem álcool / puro malte / concentração / cancelamentos de registro | Anuários MAPA 2023–2025 (células abaixo) | Brasil, anual, 3 vintages | Sem álcool 4,9%→1,27%: **quebra metodológica**. Puro malte 29,2→24,7→29,2: **três medidas de vintage** (o 24,7% não some na revisão). Nenhum dos dois entra no dashboard como tendência. |

## Ato 3 — o que dá e o que não dá para concluir

| Afirmação | Fonte primária | Grain disponível | Lacuna |
| --- | --- | --- | --- |
| GGR 2025 e destinações legais | — | — | **Fora de escopo** (ADR 0004). Não afirmar |
| ~1.144 empregos formais em 60 empregadores; R$ 1 salário / R$ 291 receita | IEPS (e/ou RAIS citado no dossiê) | setor-ano | Conferir se o IEPS cita RAIS ou estima |
| 15,5 mil empregos diretos e indiretos; R$ 7,5 bi de capital social; R$ 9 bi de arrecadação 2025 | LCA+Cruz / IBJR / ANJL, nov/2025 | setor, um corte | Associação do setor. Divergência de emprego com o IEPS |
| Custo social ~R$ 38,8 bi | IEPS | nacional, anual estimado | Modelo do IEPS, não contabilidade |
| Cerveja: 41.305 empregos na fabricação, cadeia >2 mi, R$ 27 bi massa salarial, 2% PIB, R$ 49,6 bi impostos | Anuário MAPA / CervBrasil citado no Anuário | setor-ano | Separar o que é MAPA do que é associação |
| Jovens <25: 45% consomem álcool, menor desde 1962 | MindMiners (via jornalismo/CISA?) | não está no lake como primário | **Fonte primária ausente.** Não afirmar até achar o relatório |
| GLP-1: usuários reduzem bebidas em 0,91%; mercado formal ~R$ 16 bi | Scanntech (via jornalismo) | não está no lake como primário | Hipótese rival no artigo, **fora do modelo**. Não precisa de ingestão agora |

## Divergências já mapeadas (conteúdo de `qa_divergencias`)

| Métrica | Período | Valor A | Valor B |
| --- | --- | --- | --- |
| Produção cerveja | 2024 | 15,344 bi L (pub 2025) | 17,211 bi L (pub 2026) |
| Comércio exterior | 2021–22 vs 2024+ | kg | litros (já inclui sem álcool) |
| Cerveja sem álcool | ~2024 | 757 mi L produção MAPA | ~702 mi L vendas Euromonitor (matéria) |
| Apostadores 2025 | 2025 | Klavi 3,7 mi (amostra Open Finance) | LAI ~25 mi (só via jornalismo; não é censo) |
| Tamanho de mercado bets 2025 | 2025 | EE119 Pix (um mês, fluxo bruto) | Regulus Partners US$ 4,1 bi (via Rádio Senado) |
| Emprego no setor de apostas | 2025 | IEPS ~1.144 formais / 60 empregadores | IBJR/ANJL 15,5 mil diretos e indiretos |

## Fontes no lake que não sustentam afirmação da janela

Anuários 2021 e 2022 (sem produção). Catalisi 2021 e 2022 (Euromonitor, fora da janela). CNN/iFood (evento pontual). Amaro e El Khatib (publicidade e universitários — contexto, não métrica de mercado). TCC da UFRGS (qualitativo).

## Verificações etapa 4

Respostas com citação. `pagina` / `tabela_idx` = campos do `extract.parquet` (`metodo=pdfplumber_table` ou `pdfplumber_text`).

### 1. Cerveja sem álcool na SIDRA 8885: **11.1** (`129192`)

A tabela 8885 não tem produto “cerveja” nem “cerveja zero”. Os metadados do agregado ([`/agregados/8885/metadados`](https://servicodados.ibge.gov.br/api/v3/agregados/8885/metadados)) expõem a classificação **542** “Grupos e classes industriais”, categorias **129192** “11.1 Fabricação de bebidas alcoólicas” e **129193** “11.2 Fabricação de bebidas não alcoólicas”. O Parquet `sidra_8885_pim_bebidas` confirma as duas categorias no payload (variável 12606).

A PIM-PF classifica a **unidade local** pela CNAE 2.0, não o SKU. Na CONCLA, a subclasse [1113-5/02 Fabricação de cervejas e chopes](https://concla.ibge.gov.br/busca-online-cnae.html?subclasse=1113502&view=subclasse) está no grupo **11.1** e “compreende também a fabricação de cervejas sem álcool ou com baixo teor alcoólico”. Cerveja zero de cervejaria **não** vai para 11.2 (refrigerantes / não alcoólicas).

Implicação: `producao_bebidas_alcoolicas_indice` continua o proxy mensal; inclui zero produzida em 11.1. Segundo modelo SARIMAX de zero **não** entra ([trabalho_futuro.md](trabalho_futuro.md)). Fora do dashboard: qualquer série rotulada “produção de cerveja com álcool” a partir da 8885.

### 2. Sem álcool 4,9% → 1,27%: **quebra metodológica**

Não é o denominador da retificação de 2024.

| Vintage | Célula | Fonte |
| --- | --- | --- |
| 2023 | 0,8% do volume declarado; 118.924.317,44 L (citado no vintage seguinte) | pub 2024 `pagina=46`; pub 2025 `pagina=55` |
| 2024 | 757.444.322,53 L = **4,9%** de 15.344.065.267,36 L; +536,9% vs 2023 | pub 2025 `pagina=55` (Tabela 21 no texto) |
| 2025 | **1,27%** da produção nacional; sem litros na tabela | pub 2026 `pagina=54` (só chamada; a Tabela 21 desse vintage passou a ser estilo, `pagina=55` `tabela_idx=0`) |
| 2024 retificado | 17.210.754.610,75 L (método: retificações voluntárias / auditoria) | pub 2026 `pagina=7` e `pagina=51` |

757.444.322,53 / 17.210.754.610,75 ≈ **4,4%**, não 1,27%. 1,27% × 15.688.083.191,69 L (`pagina=51`) implica numerador ≈ **199 mi L**. O numerador mudou (ou o universo da chamada mudou); a edição 2026 **não republica** a tabela de teor alcoólico. Definição legal (≤ 0,5%) é a mesma em pub 2024 `pagina=46` e pub 2025 `pagina=54`.

Fora do dashboard: série ou sparkline “mix sem álcool 2023–2025”.

### 3. Puro malte 29,2% → 24,7% → 29,2%: **três medidas de vintage**

O 24,7% **não some** na revisão de 2024. A pub 2026 não substitui o mix de 2024; só publica o de 2025.

| Ano de referência | Participação | Volume (L) | Fonte |
| --- | --- | --- | --- |
| 2023 | 29,2% | (gráfico; sem célula de litros no extract) | pub 2024 `pagina=45` |
| 2024 | 24,7% | (gráfico; sem célula de litros no extract) | pub 2025 `pagina=54` |
| 2025 | 29,20% | 4.580.310.971,90 | pub 2026 `pagina=52` `tabela_idx=1`; chamada `pagina=53` |

A Tabela 20 da pub 2026 traz variação 2024/2025 de **+21,01%** no volume de puro malte. 4.580.310.971,90 / 1,2101 ≈ 3,785 bi L, que é 24,7% de **15.344.065.267,36 L** (total *não* retificado da pub 2025 `pagina=51`), não 24,7% de 17,211 bi L. Ou seja: o YoY de mix usa o vintage 2024 original; o YoY do total usa o 2024 retificado (`pagina=7`). Definição (mosto só de malte de cevada / extrato de malte) é a mesma nos três vintages.

Fora do dashboard: V de participação puro malte e qualquer decomposição shift-share desses três pontos.

### O que não entra no dashboard (síntese)

- Mix sem álcool e V de puro malte como tendência 2023–2025.
- SIDRA 8885 como produção de “cerveja com álcool” ou como série de cerveja zero.
- Segundo contrafactual SARIMAX para zero.

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
| Série mensal de bebidas alcoólicas estável o bastante para o contrafactual cair no IC | SIDRA 8885 | Brasil, mensal, índice | **API ainda não ingestada.** Verificar classificação da cerveja sem álcool (11.1 vs 11.2) |

## Ato 2 — de onde saiu o dinheiro

| Afirmação | Fonte primária | Grain disponível | Lacuna |
| --- | --- | --- | --- |
| 52% poupança; 48% bares/restaurantes/delivery; 43% roupas; 41% cultura | Strategy& / Locomotiva, p. 19 | survey classes C/D/E, um corte | **Não é cerveja.** Ponte on-premise. Amostra de survey, tier C |
| Apostas 0,73% → 1,38% do orçamento nas classes D/E; +419% desde 2018 | mesmo relatório | classe, anual até 2023/24 | Série para antes da janela; usar como nível, não como tendência 2023–26 |
| Razão apostas/alimentação 1,5%→4,9%; apostas/lazer 10%→36% | mesmo relatório | nacional, dois pontos | — |
| Mediana R$ 100 ≡ 16,7% do Bolsa Família; PCE 1,0→0,83 | Fundaj NT39 | PBF, recorte nacional | — |
| 5 mi beneficiários PBF, R$ 3 bi em ago/2024, 70% chefes de família | BCB EE119 | mês, PBF | Um mês só. Não é série |
| 3,7 mi apostadores Klavi em 2025 (dobro de 2024); 18% alto risco | Klavi (HTML próprio + Valor Investe) | amostra Open Finance | Não é censo. Não tratar como total nacional |
| Mix sem álcool / puro malte / concentração / cancelamentos de registro | Anuários MAPA 2023–2025 | Brasil, anual, 3 pontos | V de puro malte e queda de sem álcool 4,9%→1,27% são **suspeitas de artefato de revisão**. Bloqueante |

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

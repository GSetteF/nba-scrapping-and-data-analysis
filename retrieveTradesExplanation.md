# Extração e Estruturação das Transações da NBA

As transações da NBA são disponibilizadas no Basketball Reference em formato textual semi-estruturado, combinando linguagem natural com marcação HTML (links para equipes e jogadores). Essas descrições incluem operações como trocas (trades), contratações (signings) e dispensas (waivers). Para possibilitar análises quantitativas, é necessário transformar essas descrições em um formato tabular estruturado.

Neste projeto, cada troca (trade) é convertida em múltiplas linhas de uma tabela, onde cada linha representa um ativo movimentado (jogador, escolha de draft ou dinheiro). Todas as linhas pertencentes à mesma operação compartilham um identificador comum (`trade_id`). O escopo principal é a análise de trocas entre franquias, sendo as demais operações descartadas na etapa de parsing.

---

## 1. RESULTADO FINAL

O arquivo (nba_trades_1950_2026.csv) gerado pelo pipeline apresenta as seguintes características:

* **Total de registros**: 8819 linhas
* **Trades distintos (`trade_id` únicos)**: 8819
* **Ativos do tipo `player`**: 6380 (72,3%)
* **Ativos do tipo `pick`**: 2439 (27,7%)
* **Operações com trade exception**: 1144
* **Franquias envolvidas**: 61
* **Período coberto**: Set. 1949 – Fev. 2026

---

## 2. ESTRUTURA DOS DADOS

Cada registro contém as seguintes variáveis:

* **trade_id**: Identificador numérico único que agrupa todos os ativos de uma mesma troca - Inteiro (int)
* **date**: Data de oficialização da negociação (`YYYY-MM-DD`) - Data
* **operation_type**: Tipo da operação (sempre `trade` neste dataset) - String
* **team_from**: Sigla da equipe que enviou o ativo - String
* **team_to**: Sigla da equipe que recebeu o ativo - String
* **asset_type**: Tipo do ativo: `player`, `pick` ou `cash` - Categórico
* **asset_name**: Nome do jogador, descrição do pick ou valor em dinheiro - String
* **pick_year**: Ano da escolha de draft (quando aplicável) - Inteiro (int)
* **pick_round**: Rodada da escolha (1 ou 2; quando aplicável) - Inteiro (int)
* **pick_original_team**: Equipe originalmente dona da escolha (quando disponível) - String
* **has_trade_exception**: Indica se a operação envolve exceção salarial de troca - Booleano

Campos não aplicáveis (ex: `pick_year` quando o ativo é um jogador) são preenchidos com `None`, garantindo consistência para análises posteriores.

---

## 3. ESTRATÉGIA DE PROCESSAMENTO

O processamento é feito diretamente sobre a estrutura HTML da página de transações de cada temporada (`/leagues/NBA_{ano}_transactions.html`), explorando o fato de que:

* Equipes aparecem como hyperlinks do tipo `/teams/...`
* Jogadores aparecem como hyperlinks do tipo `/players/...`
* Escolhas de draft e dinheiro aparecem como texto puro

Essa abordagem baseada em links HTML reduz ambiguidades em relação a nomes próprios e permite separar os componentes da transação com maior robustez do que processar texto puro.

### 3.1 Coleta do HTML

Para cada temporada entre 1950 e 2026, o HTML da página de transações é baixado via `cloudscraper`, que simula requisições de navegador para contornar bloqueios. Comentários HTML (`<!-- -->`) são removidos para expor o conteúdo oculto. Uma pausa de 3 segundos é aplicada entre requisições para respeitar o rate limit do servidor.

### 3.2 Parsing das Datas

As datas são extraídas dos elementos `<span>` dentro de cada bloco `<li>`. Dois formatos são tratados:

- Formato padrão: `"February 23, 2026"` → `2026-02-23`
- Formato com dia desconhecido: `"August ?, 1949"` → substituído por `"August 01, 1949"`

### 3.3 Identificação das Trades

Apenas parágrafos `<p>` cujo texto contém o verbo `"traded"` são processados. Operações como `signed` e `waived` são descartadas.

### 3.4 Decomposição em Subtransações

Descrições de trades envolvendo múltiplas equipes são separadas por ponto e vírgula (`;`), preservando os links HTML de cada segmento. Cada segmento é tratado como uma subtransação independente do tipo:

(EQUIPE_ORIGEM traded ATIVOS to EQUIPE_DESTINO)

### 3.5 Extração das Equipes e Ativos

* **Equipes**: `team_from` e `team_to` são identificados pelos links `/teams/` dentro de cada segmento, na ordem em que aparecem no HTML.
* **Jogadores**: identificados por links `/players/`
* **Picks**: extraídos por expressão regular sobre o texto (`\d{4} .*?draft pick`)
* **Dinheiro (cash)**: identificado por palavras-chave no texto

### 3.6 Normalização de Equipes

Os nomes completos das franquias são convertidos para siglas de três letras via dicionário de mapeamento (ex: `"Boston Celtics"` -> `"BOS"`). Franquias históricas extintas ou relocadas são mapeadas para suas siglas originais de época.

### 3.7 Detecção de Trade Exceptions

A presença da expressão `"trade exception"` no texto original do parágrafo é usada para preencher o campo `has_trade_exception`.

---

## 4. LIMITAÇÕES CONHECIDAS

* **Picks sem interpretação semântica**: cláusulas de proteção (ex: "top-5 protected", "did not convey", "right to swap") são mantidas como texto no campo `asset_name`, mas não são interpretadas. Isso não compromete a identificação das equipes envolvidas, apenas a análise detalhada do valor dos picks.
* **Jogadores citados como consequência de picks**: em algumas transações, o texto menciona jogadores posteriormente selecionados com um pick trocado. Esses nomes aparecem no texto mas não representam ativos efetivamente trocados e não são incluídos como registros.
* **Cash sem valor monetário**: quando o ativo é `"cash"`, o campo `asset_name` registra apenas `"cash"` sem valor específico, pois o Basketball Reference não disponibiliza os montantes.
* **Gaps pontuais**: a combinação de rate limiting e possíveis instabilidades do servidor pode ter resultado em ausências isoladas em temporadas específicas, especialmente nas décadas de 1950 e 1960.

Essas limitações não comprometem a estrutura principal das trocas (quais equipes trocaram quais ativos), que é o objetivo analítico central do projeto.
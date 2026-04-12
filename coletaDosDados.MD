# Coleta dos Dados: Análise de Impacto das Trades na NBA (1950-2025)

**Disciplina**: Introdução a Ciência de Dados

**Professor**: Yuri de Almeida Malheiros Barbosa 

**Alunos**: Gabriel Sette de Figueirêdo, Jocyneide Bernardo da Silva e Milton Bezerra Do Vale Filho

---

## 1. OBJETIVO DO PROJETO
Este projeto tem como objetivo coletar, estruturar e analisar dados históricos da NBA para medir o impacto das trocas de jogadores (trades) na performance das equipes. A análise busca identificar se as movimentações de mercado resultam em melhorias imediatas ou graduais e o que caracteriza uma troca bem-sucedida.

## 2. PROCESSO DE COLETA E ESTRUTURAÇÃO

A coleta de dados foi realizada por meio de Web Scraping no site Basketball Reference, utilizando Python. O processo foi dividido em múltiplos pipelines independentes, cada um responsável por um tipo específico de dado (jogos, estatísticas de jogadores, resultados de temporada e transações).

### 2.1 Estratégia Geral

- Utilização da biblioteca `cloudscraper` para simular requisições de navegador e contornar bloqueios do site.
- Parsing do HTML com `BeautifulSoup`, incluindo tratamento de tabelas comentadas (remoção de `<!-- -->`).
- Extração tabular com `pandas.read_html`.
- Implementação de mecanismos de resiliência:
  - Sistema de retries para falhas de requisição
  - Tratamento explícito de erro HTTP 429 (rate limit)
  - Pausas aleatórias entre requisições para evitar bloqueios
- Armazenamento dos dados em arquivos CSV organizados por tipo e temporada.

---

### 2.2 Coleta de Estatísticas de Jogadores

Os dados de performance individual foram coletados para todas as temporadas entre 1950 e 2025, incluindo temporada regular e playoffs.

- Fonte: páginas de estatísticas avançadas por temporada
- Duas coletas por ano:
  - Temporada regular
  - Playoffs
- Cada conjunto recebe uma flag `is_playoff` para diferenciação
- Os dados são concatenados e salvos por temporada

Tratamentos aplicados:
- Remoção de linhas duplicadas de cabeçalho
- Conversão automática de tipos numéricos quando possível
- Padronização com colunas `season` e `is_playoff`

---

### 2.3 Coleta de Jogos por Equipe

A coleta de jogos foi feita por equipe e por temporada.

Etapas do processo:

1. Identificação das equipes participantes de cada temporada:
   - Extração automática a partir da página da liga
   - Fallback com dicionário manual para equipes históricas

2. Coleta dos jogos:
   - Acesso à página específica de cada time na temporada
   - Extração de:
     - Jogos da temporada regular
     - Jogos de playoffs (quando disponíveis)

3. Estruturação:
   - Inclusão das colunas `team` e `season`
   - Criação da flag `is_playoff`
   - Remoção de linhas inválidas ou vazias

4. Armazenamento:
   - Um arquivo CSV por time por temporada

---

### 2.4 Coleta de Resultados das Temporadas

Os resultados agregados das equipes foram extraídos a partir das páginas de playoffs.

Estratégia:

- Parsing da tabela de confrontos dos playoffs
- Identificação dos vencedores e perdedores de cada série
- Construção de três conjuntos:
  - Times que chegaram aos playoffs
  - Times que chegaram às finais de conferência
  - Campeão da temporada

Processamento adicional:

- Conversão dos nomes das equipes para suas siglas
- Geração de registros para equipes que não participaram dos playoffs (valores 0)
- Consolidação final em um único dataset

Variáveis finais:
- reached_playoffs
- reached_conf_finals
- champion

---

### 2.5 Coleta e Estruturação de Trades

As transações da NBA são disponibilizadas em formato textual semi-estruturado. Para permitir análise quantitativa, foi necessário transformá-las em formato tabular.

Estratégia adotada:

- Processamento direto do HTML das páginas de transações
- Uso da estrutura dos hyperlinks para identificação:
  - Equipes: links `/teams/`
  - Jogadores: links `/players/`

Etapas:

1. Filtragem:
   - Apenas operações contendo "traded" são consideradas

2. Decomposição:
   - Separação de descrições complexas em múltiplas subtransações

3. Extração:
   - team_from e team_to a partir dos links
   - ativos identificados individualmente

4. Estruturação:
   - Cada ativo ocupa uma linha
   - Todas as linhas da mesma troca compartilham um `trade_id`

Limitações:
- Cláusulas complexas de picks não são interpretadas semanticamente
- Jogadores citados indiretamente não são considerados ativos principais
- Só foi realizado tratamento de `trades` como definido no escopo do projeto, podendo expandir futuramente para outros ativos como `picks` ou `cash`.

**OBS:** Temos outro documento explicando somente esse processo (por ser o principal do nosso trabalho), ele não está completamente atualizado mas incluimos ele no repositório caso deseje ler.

---

## 3. CONJUNTO DE DADOS

Os quatro conjuntos de dados utilizados no projeto foram coletados via web scraping do Basketball Reference, cobrindo 76 temporadas (1950-2025). A tabela a seguir mostra um resumo de comparação:

| Tabela | Registros | Cobertura temporal | Granularidade |
|---|---|---|---|
| `nba_trades_1950_2026` | 8.819 linhas | 1949–2026 | Um ativo por linha |
| `team_season_outcomes` | 4.332 linhas | 1950–2025 | Um time por temporada |
| `PlayerSeasonStats` | ~75 arquivos CSV | 1950–2025 | Um jogador por temporada |
| `TeamGames` | ~1.800 arquivos CSV | 1950–2025 | Um jogo por linha |

### 3.1. Tabela: TeamGames
Contém o histórico de todas as partidas disputadas pelas franquias. Os dados são armazenados em arquivos individuais no formato ({sigla}_{ano}_games.csv), resultando em aproximadamente 1800 arquivos no total. 

**Campos e Descrições:**
* **G**: Número sequencial do jogo na temporada - Inteiro (int) 
* **Date**: Data da realização da partida - Data/String 
* **Start (ET)**: Horário de início do jogo no fuso do leste dos EUA - String (tempo) 
* **Opponent**: Nome da equipe adversária - String 
* **Unnamed: 5 (@)**: Indica se o jogo foi realizado fora de casa (marcado com @) - String / Categórico 
* **Tm**: Pontos marcados pelo time analisado - Inteiro (int) 
* **Opp**: Pontos marcados pelo adversário - Inteiro (int) 
* **W**: Total acumulado de vitórias na temporada - Inteiro (int) 
* **L**: Total acumulado de derrotas na temporada - Inteiro (int) 
* **Streak**: Sequência atual de resultados (Ex: "W 4", "L 2") - String 
* **Attend.**: Público total presente no ginásio - Inteiro (int) 
* **LOG**: Duração total da partida (hh:mm) - String (tempo) 
* **Notes**: Observações adicionais sobre o confronto - String (opcional) 
* **is_playoff**: Indica se a partida pertence à fase de playoffs - Booleano 
* **team**: Sigla identificadora do time - String 
* **season**: Ano correspondente à temporada - Inteiro (int) 

**Exemplo de Dados:**
| G | Date | Start (ET) | Unnamed: 3 | Unnamed: 4 | @ | Opponent | Unnamed: 7 | Unnamed: 8 | Tm | Opp | W | L | Streak | Attend. | LOG | Notes | is_playoff | team | season |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 17 | Thu, Jun 5, 2025 | 8:30p | | Box Score | | Indiana Pacers | L | | 110 | 111 | 12 | 5 | L 1 | 18203 | 2:30 | | True | OKC | 2025 |
| 18 | Sun, Jun 8, 2025 | 8:00p | | Box Score | | Indiana Pacers | W | | 123 | 107 | 13 | 5 | W 1 | 18203 | 2:29 | | True | OKC | 2025 |
| 19 | Wed, Jun 11, 2025 | 8:30p | | Box Score | @ | Indiana Pacers | L | | 107 | 116 | 13 | 6 | L 1 | 17274 | 2:36 | | True | OKC | 2025 |
| 20 | Fri, Jun 13, 2025 | 8:30p | | Box Score | @ | Indiana Pacers | W | | 111 | 104 | 14 | 6 | W 1 | 17274 | 2:49 | | True | OKC | 2025 |
| 21 | Mon, Jun 16, 2025 | 8:30p | | Box Score | | Indiana Pacers | W | | 120 | 109 | 15 | 6 | W 2 | 18203 | 2:36 | | True | OKC | 2025 |
| 22 | Thu, Jun 19, 2025 | 8:30p | | Box Score | @ | Indiana Pacers | L | | 91 | 108 | 15 | 7 | L 1 | 17274 | 2:30 | | True | OKC | 2025 |
| 23 | Sun, Jun 22, 2025 | 8:00p | | Box Score | | Indiana Pacers | W | | 103 | 91 | 16 | 7 | W 1 | 18203 | 2:40 | | True | OKC | 2025 |

**Legenda**: Jogos das finais da temporada de 2025 do Oklahoma City Thunder.

---

### 3.2. Tabela: PlayerSeasonStats
Reúne estatísticas gerais e métricas avançadas de performance individual dos jogadores ao longo das temporadas. Os dados foram armazenados em arquivos que foram separados por temporada (ex: player_season_stats_2020.csv), tendo a flag (is_playoff) para diferenciar a temporada regular dos playoffs.

**Campos e Descrições:**
* **Rk**: Ranking do jogador na listagem da temporada - Inteiro (int) 
* **Player**: Nome completo do jogador - String 
* **Pos**: Posição principal ocupada em quadra (C, PF, SG, etc.) - Categórico (string) 
* **Age**: Idade do atleta na temporada - Inteiro (int) 
* **Tm**: Sigla do time defendido - String 
* **G**: Total de jogos disputados - Inteiro (int) 
* **MP**: Total de minutos jogados na temporada - Inteiro (int) 
* **season**: Ano da temporada - Inteiro (int) 
* **is_playoff**: Indica se as estatísticas referem-se aos playoffs - Booleano 
* **PER (Player Efficiency Rating)**: Medida de produtividade por minuto, padronizada para que a média da liga seja 15.0 - Float 
* **TS% (True Shooting Percentage)**: Eficiência de arremesso que considera cestas de 2 pontos, 3 pontos e lances livres - Float 
* **3PAr**: Proporção de tentativas de arremesso que são de 3 pontos - Float 
* **FTr**: Taxa de lances livres cobrados por tentativa de arremesso de quadra - Float 
* **ORB% / DRB% / TRB%**: Porcentagem estimada de rebotes disponíveis que o jogador agarrou (Ofensivos, Defensivos e Totais) - Float 
* **AST%**: Porcentagem estimada de cestas de quadra do time que o jogador assistiu enquanto estava em quadra - Float 
* **STL% / BLK%**: Porcentagem estimada de posses de bola do adversário terminadas por roubo ou toco do jogador - Float 
* **TOV%**: Estimativa de turnovers cometidos por cada 100 posses de bola - Float 
* **USG% (Usage Percentage)**: Porcentagem estimada de jogadas do time finalizadas pelo jogador enquanto ele estava em quadra - Float 
* **OWS / DWS**: Estimativa do número de vitórias contribuídas pelo jogador devido ao seu desempenho ofensivo e defensivo - Float 
* **WS (Win Shares)**: Estimativa do número total de vitórias atribuídas ao jogador na temporada - Float 
* **WS/48**: Contribuição de Win Shares por cada 48 minutos de jogo - Float 
* **OBPM / DBPM**: Estimativa de pontos por 100 posses que o jogador contribui acima da média da liga (Ataque e Defesa) - Float 
* **BPM (Box Plus/Minus)**: Métrica de impacto total do jogador por 100 posses em relação à média da liga - Float 
* **VORP (Value Over Replacement Player)**: Impacto total do jogador em relação a um jogador de nível reserva médio (substituição) - Float 

**Observação**: estatísticas avançadas (PER, BPM, VORP) podem estar incompletas para temporadas anteriores a 1974, pois é um período com cobertura limitada no Basketball Reference.

**Exemplo de Dados:**
| Rk | Player | Pos | Age | Tm | G | MP | PER | TS% | 3PAr | FTr | ORB% | DRB% | TRB% | AST% | STL% | BLK% | TOV% | USG% | Unnamed: 19 | OWS | DWS | WS | WS/48 | Unnamed: 24 | OBPM | DBPM | BPM | VORP | season | is_playoff | 
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 58 | Shai Gilgeous-Alexander | PG | 26 | OKC | 23 | 851 | 25.3 | 0.574 | 0.224 | 0.431 | 2.9 | 12.9 | 7.9 | 30.6 | 2.2 | 2.4 | 9.1 | 32.9 | | 2.6 | 1.4 | 3.9 | 0.222 | | 5.7 | 2.6 | 8.3 | 2.2 | 2025 | True | 
| 95 | LeBron James | SF | 40 | LAL | 5 | 204 | 25.5 | 0.601 | 0.318 | 0.455 | 7.0 | 18.3 | 12.8 | 26.9 | 2.6 | 4.3 | 11.0 | 27.2 | | 0.6 | 0.2 | 0.8 | 0.198 | | 6.9 | 2.7 | 9.5 | 0.6 | 2025 | True | 
| 3 | Bam Adebayo | C | 27 | MIA | 4 | 153 | 15.9 | 0.508 | 0.328 | 0.172 | 11.7 | 23.4 | 17.1 | 19.4 | 1.4 | 0.8 | 14.8 | 24.5 | | 0.0 | -0.2 | -0.2 | -0.066 | | 0.7 | -1.5 | -0.9 | 0.0 | 2025 | True | 
| 8 | Giannis Antetokounmpo | PF | 30 | MIL | 5 | 188 | 33.2 | 0.651 | 0.051 | 0.636 | 11.0 | 38.0 | 23.6 | 35.6 | 1.3 | 2.6 | 15.4 | 35.3 | | 0.8 | 0.1 | 0.9 | 0.232 | | 8.2 | 3.2 | 11.4 | 0.6 | 2025 | True | 

**Legenda**: Algumas estatísticas de jogadores na temporada 2025.

---

### 3.3. Tabela: TeamSeasonOutcomes
Consolida os resultados alcançados por cada time por ano, conta com `4332 registros` que cobrem `57 franquias` ao longo de 76 temporadas (1950-2025). Para as equipes que não participaram dos playoffs em uma temporada, os campos recebem o valor booleano 0, o que garante um dataset sem registros ausentes.

**Campos e Descrições:**
* **team**: Sigla identificadora do time - String 
* **season**: Ano correspondente à temporada - Inteiro (int) 
* **reached_playoffs**: Indica se a equipe se classificou para a pós-temporada - Booleano 
* **reached_conf_finals**: Indica se a equipe disputou as Finais de Conferência - Booleano 
* **champion**: Indica se a equipe conquistou o título da temporada - Booleano 

**Exemplo de Dados:**
| team | season | reached_playoffs | reached_conf_finals | champion |
|---|---|---|---|---|
| BOS | 2020 | True | True | False | 
| BOS | 2021 | True | False | False | 
| BOS | 2022 | True | True | False | 
| BOS | 2023 | True | True | False | 
| BOS | 2024 | True | True | True |

**Legenda**: Resultados do Boston Celtics ao longo de múltiplas temporadas.

---

### 3.4. Tabela: nba_trades_1950_2026
Dicionário estruturado de todas as movimentações de trocas entre franquias, conta com `8819 registros`, sendo `6380 ativos do tipo player (72,3%)` e `2439 picks (27,7%)`, envolvendo `61 franquias` durante o período de setembro de 1949 a fevereiro de 2026.

**Campos e Descrições:**
* **operation_type**: Tipo da transação realizada (Ex: trade) - String 
* **team_from**: Equipe que cedeu o ativo na negociação - String 
* **team_to**: Equipe que recebeu o ativo na negociação - String 
* **asset_type**: Categoria do ativo movimentado (player, pick ou cash) - String 
* **asset_name**: Nome do jogador, descrição da escolha de draft ou valor em dinheiro - String 
* **pick_year**: Ano da escolha de draft envolvida (se aplicável) - Inteiro (int)
* **pick_round**: Rodada correspondente da escolha de draft - Inteiro (int)
* **pick_original_team**: Time dono original da escolha de draft - String
* **has_trade_exception**: Indica se a operação gerou uma exceção de troca salarial - Booleano 
* **trade_id**: Identificador numérico único que agrupa todos os ativos de uma mesma troca - Inteiro (int) 
* **date**: Data em que a negociação foi oficializada - Data 

**Exemplo de Dados:**
| operation_type | team_from | team_to | asset_type | asset_name | pick_year | pick_round | pick_original_team | has_trade_exception | trade_id | date |
|---|---|---|---|---|---|---|---|---|---|---|
| trade | DAL | LAL | player | Luka Doncic | | | | True | 8483 | 2025-02-02  |
| trade | DAL | LAL | player | Maxi Kleber | | | | True | 8484 | 2025-02-02  |
| trade | DAL | LAL | player | Markieff Morris | | | | True | 8485 | 2025-02-02  |
| trade | LAL | DAL | player | Max Christie | | | | True | 8486 | 2025-02-02  |
| trade | LAL | DAL | player | Anthony Davis | | | | True | 8487 | 2025-02-02  |
| trade | LAL | DAL | pick | 2029 1st round draft pick | | | | True | 8488 | 2025-02-02  |
| trade | LAL | UTA | player | Jalen Hood-Schifino | | | | True | 8489 | 2025-02-02  |
| trade | LAL | UTA | player | John Tonje | | | | True | 8490 | 2025-02-02  |
| trade | LAL | UTA | pick | 2025 2nd round draft pick | | | | True | 8491 | 2025-02-02  |
| trade | UTA | DAL | pick | 2025 2nd round draft pick | | | | True | 8492 | 2025-02-02  |

**Legenda**: Troca entre três times da NBA: Los Angeles Lakers, Dallas Mavericks e Utah Jazz.

### 3.5. Limitações e Considerações

* **Escopo de ativos**: apenas trades com jogadores e picks foram mapeados. Operações envolvendo somente dinheiro (cash considerations) são subrepresentadas ou omitidas.
* **Picks sem proteções**: as cláusulas de proteção (ex: "top-5 protected") estão presentes no campo `asset_name` como texto, mas não ffoi possível que fossem interpretadas semanticamente.
* **Franquias históricas**: times extintos ou relocados (ex: Seattle SuperSonics, Vancouver Grizzlies) aparecem com suas siglas históricas, necessitando um mapeamento adicional em análises verticais.
* **Estatísticas pré-1974**: campos como PER, BPM e VORP podem estar incompletos para temporadas antecedentes a esse período.
* **Rate limiting**: pausas aleatórias e tratamento de erro HTTP 429 foram implementados para respeitar os limites do servidor, podendo ter gerado lacunas pontuais em temporadas específicas.

**Todos os dados estão disponíveis nesse Repositório**
🏀 Extração e Estruturação das Transações da NBA

As transações da NBA são disponibilizadas no Basketball Reference em formato textual semi-estruturado, combinando linguagem natural com marcação HTML (links para equipes e jogadores). Essas descrições incluem operações como trocas (trades), contratações (signings) e dispensas (waivers). Para possibilitar análises quantitativas, é necessário transformar essas descrições em um formato tabular estruturado.

Neste projeto, cada troca (trade) é convertida em múltiplas linhas de uma tabela, onde cada linha representa um ativo movimentado (jogador, escolha de draft ou dinheiro). Todas as linhas pertencentes à mesma operação compartilham um identificador comum (trade_id).

O escopo principal do trabalho é a análise de trocas entre franquias (trades), sendo as demais operações ignoradas na etapa de parsing final.

📐 Estrutura dos dados

Cada registro contém as seguintes variáveis:

trade_id: identificador da operação

date: data da transação

operation_type: tipo da operação (trade)

team_from: equipe que enviou o ativo

team_to: equipe que recebeu o ativo

asset_type: tipo do ativo (player, pick ou cash)

asset_name: descrição textual do ativo

pick_year: ano da escolha de draft (quando aplicável)

pick_round: rodada da escolha (1 ou 2, quando aplicável)

pick_original_team: equipe originalmente dona da escolha (quando disponível)

has_trade_exception: indica se a operação envolve exceção de troca (trade exception)

🧠 Estratégia de processamento

O processamento é realizado diretamente sobre a estrutura HTML da página de transações, explorando o fato de que:

Equipes aparecem como hyperlinks do tipo /teams/...

Jogadores aparecem como hyperlinks do tipo /players/...

Escolhas de draft e dinheiro aparecem como texto puro

Essa abordagem reduz ambiguidades em relação a nomes próprios e permite separar com maior robustez os componentes da transação.

O método segue as seguintes etapas:

Identificação de trades
Apenas descrições que contêm o verbo traded são consideradas. Operações como signings e waivers são descartadas.

Decomposição em subtransações
Descrições complexas são divididas em blocos do tipo:

TEAM traded ASSETS to TEAM
possibilitando o tratamento de trocas envolvendo múltiplas equipes.

Extração das equipes
As equipes de origem (team_from) e destino (team_to) são identificadas a partir dos hyperlinks HTML.

Extração dos ativos

Jogadores: identificados por links para /players/

Escolhas de draft: extraídas por expressões regulares sobre o texto

Dinheiro (cash): identificado por palavras-chave no texto

Classificação dos ativos
Cada ativo é classificado como:

player

pick

cash

Tratamento de metadados
A presença de trade exceptions é detectada por meio da busca da expressão “trade exception” no texto original.

Representação de valores ausentes
Campos não aplicáveis (por exemplo, pick_year quando o ativo é um jogador) são preenchidos com None, garantindo consistência para análises posteriores.

⚠️ Limitações conhecidas

Jogadores citados apenas como consequência da escolha de draft (por exemplo, “(Player X was later selected)”) podem aparecer no texto, mas não representam ativos efetivamente trocados. Esses casos são tratados como metadados e não fazem parte da troca principal.

Cláusulas jurídicas detalhadas de picks (como right to swap, did not convey ou proteções) não são semanticamente interpretadas, sendo mantidas apenas como parte do texto do ativo quando necessário.

Essas limitações não comprometem a estrutura da troca (quais equipes trocaram quais ativos), que é o principal objetivo analítico do projeto.

🎯 Objetivo final

A abordagem proposta transforma descrições textuais complexas em um conjunto de dados estruturado, adequado para:

análises estatísticas de volume de trocas,

modelagem de redes de transferências entre franquias,

estudos longitudinais sobre comportamento das equipes ao longo das temporadas,

investigações sobre o papel de escolhas de draft nas negocções da NBA.
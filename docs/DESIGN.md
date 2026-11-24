# DESIGN.md — Streaming Recommendation

## 1. Princípios de design

1. **Comece pela busca:** a busca é a ação principal e deve ser o elemento mais evidente da Home.
2. **Ajude a decidir:** mostre afinidade, títulos correspondentes e preço com hierarquia clara; não transforme resultados em vitrine promocional.
3. **Reduza o ruído:** use poucos elementos por tela, rótulos diretos e espaços consistentes.
4. **Explique estados e dados:** informe o que aconteceu, o que falta fazer e quando o preço foi conferido.
5. **Seja independente de marcas:** a identidade visual é do produto; serviços aparecem apenas como texto em etiquetas coloridas.

## 2. Tokens visuais

### 2.1 Cores

| Token | Hex | Uso |
|---|---|---|
| `background` | `#0B0B0D` | Fundo principal |
| `surface` | `#18181C` | Cards, painéis e caixas de conteúdo |
| `surface-raised` | `#202025` | Superfície de foco, hover e agrupamentos dentro de cards |
| `border` | `#2A2A30` | Bordas e separadores |
| `text-primary` | `#F5F5F1` | Títulos e texto principal |
| `text-secondary` | `#A3A3A8` | Texto auxiliar e conteúdo secundário |
| `text-tertiary` | `#96969B` | Legendas essenciais e metadados; não usar `#6E6E74` para texto pequeno |
| `accent` | `#E50914` | Ação primária, seleção e marca |
| `accent-hover` | `#C8101A` | Hover/pressed de ações primárias |
| `accent-gradient-start` | `#E50914` | Início do degradê do símbolo/elementos de marca |
| `accent-gradient-end` | `#FF4B3E` | Fim do degradê; usar em decoração, não como fundo de texto pequeno |
| `genre-bg` | `#26262B` | Fundo de chips de gênero |
| `genre-text` | `#DCDCE0` | Texto de chip de gênero |
| `focus-ring` | `#FF8A82` | Anel de foco visível |
| `success` | `#39B980` | Confirmações |
| `warning` | `#F0B44D` | Avisos que não bloqueiam |
| `error` | `#FF6B6B` | Erros; sempre acompanhado de texto/ícone |
| `stream-netflix` | `#B20710` | Etiqueta Netflix; borda `#FF8A82` para distingui-la da cor primária (ver nota) |
| `stream-prime` | `#00A8E1` | Etiqueta Prime Video; texto escuro (`#0B0B0D`, 7,2:1) |
| `stream-max` | `#002BE7` | Etiqueta Max |
| `stream-globoplay` | `#FB4E22` | Etiqueta Globoplay; texto escuro (`#0B0B0D`, 5,8:1) |
| `stream-disney` | `#113CCF` | Etiqueta Disney+ |
| `stream-apple` | `#6E6E73` | Etiqueta Apple TV+; combinar com texto branco e borda |
| `stream-paramount` | `#0064FF` | Etiqueta Paramount+ |
| `stream-default` | `#4A4A52` | Etiqueta de serviço sem cor específica |

**Regras para cores de serviço:** não use logotipos, símbolos ou fontes de terceiros. O nome é sempre texto. Para a etiqueta Netflix, diferencie visualmente da ação primária com fundo mais escuro (`#B20710`), borda clara e sem brilho vermelho; a diferença não deve depender só da cor. Se o texto branco não atingir AA sobre a cor de uma etiqueta, use fundo mais escuro derivado dessa cor ou texto escuro, e valide o par antes da implementação.

> **Nota de implementação:** a versão original deste guia pedia `NETFLIX` em caixa alta na tabela de tokens, mas "manter tipografia comum" na tabela de classes. Adotamos a segunda opção: fundo `#B20710` + borda `#FF8A82`, com o nome escrito normalmente.

### 2.2 Tipografia

Usar a fonte padrão sem serifa disponível no tema do Streamlit; não carregar fonte externa nem exigir build.

| Elemento | Tamanho | Peso | Uso |
|---|---:|---:|---|
| Nome da marca na Home | 36–44 px | 700 | Título principal, somente no estado inicial |
| Título da página | 28–32 px | 700 | Home pós-busca e títulos das demais telas |
| Título de seção | 20–24 px | 600–700 | “Como funciona”, grupos e seções |
| Título de filme / streaming | 16–18 px | 600 | Card de filme e item do ranking |
| Corpo | 14–16 px | 400 | Texto geral e descrição |
| Rótulo / botão / chip | 13–14 px | 500–600 | Controles e etiquetas |
| Legenda / metadado | 12–13 px | 400 | Ano, data de conferência, observações |

Em celular, reduzir o nome da marca para 30–34 px e o título de página para 24–28 px. Evitar corpo abaixo de 14 px.

### 2.3 Espaçamento, raios e sombras

Usar escala base de 4 px:

| Token | Valor | Aplicação |
|---|---:|---|
| `space-1` | 4 px | Distância entre ícone e rótulo |
| `space-2` | 8 px | Chips e agrupamentos compactos |
| `space-3` | 12 px | Espaçamento interno pequeno |
| `space-4` | 16 px | Padding padrão de cards e controles |
| `space-6` | 24 px | Intervalo entre grupos |
| `space-8` | 32 px | Intervalo entre seções |
| `space-12` | 48 px | Respiro principal da Home |

| Token | Valor | Aplicação |
|---|---:|---|
| `radius-base` | `0.75rem` | Cards, campos e botões |
| `radius-small` | `0.5rem` | Chips |
| `radius-search` | `999px` | Barra de busca |
| `radius-pill` | `999px` | Etiquetas totalmente arredondadas |

Sombras são sutis e reservadas a foco/elevação:

- Card: `0 4px 16px rgba(0, 0, 0, 0.18)`.
- Busca focada: `0 0 0 3px rgba(255, 138, 130, 0.22), 0 0 24px rgba(229, 9, 20, 0.18)`.
- Nunca usar brilho permanente em cards ou etiquetas.

### 2.4 Contraste WCAG AA

WCAG AA exige pelo menos **4,5:1** para texto normal e **3:1** para texto grande (a partir de 24 px regular ou 18,66 px em negrito). Os índices abaixo foram calculados para as combinações listadas.

| Texto | Fundo | Contraste | Resultado |
|---|---|---:|---|
| `#F5F5F1` | `#0B0B0D` | 17,99:1 | AA/AAA |
| `#F5F5F1` | `#18181C` | 16,20:1 | AA/AAA |
| `#A3A3A8` | `#18181C` | 7,05:1 | AA/AAA |
| `#96969B` | `#18181C` | 6,01:1 | AA |
| `#DCDCE0` | `#26262B` | 11,01:1 | AA/AAA |
| `#FFFFFF` | `#E50914` | 4,79:1 | AA |
| `#FFFFFF` | `#FF4B3E` | 3,32:1 | AA apenas para texto grande |
| `#FFFFFF` | `#B20710` | 7,17:1 | AA/AAA (etiqueta Netflix) |
| `#0B0B0D` | `#00A8E1` | 7,20:1 | AA/AAA (etiqueta Prime Video) |
| `#0B0B0D` | `#FB4E22` | 5,82:1 | AA (etiqueta Globoplay) |
| `#FFFFFF` | `#002BE7` | 8,40:1 | AA/AAA (etiqueta Max) |
| `#FFFFFF` | `#113CCF` | 8,17:1 | AA/AAA (etiqueta Disney+) |
| `#FFFFFF` | `#6E6E73` | 5,07:1 | AA (etiqueta Apple TV+) |
| `#FFFFFF` | `#0064FF` | 4,92:1 | AA (etiqueta Paramount+) |
| `#FFFFFF` | `#4A4A52` | 8,78:1 | AA/AAA (etiqueta padrão) |

Texto `#6E6E74` não atinge AA para texto pequeno em fundos escuros: substituir por `#96969B` ou mais claro. Recalcular contrastes se qualquer token, opacidade, cor de etiqueta ou tamanho do texto mudar. Não usar transparência para texto essencial.

## 3. Mapeamento para Streamlit

### 3.1 Tema `.streamlit/config.toml`

```toml
[theme]
base = "dark"
primaryColor = "#E50914"
backgroundColor = "#0B0B0D"
secondaryBackgroundColor = "#18181C"
textColor = "#F5F5F1"
borderColor = "#2A2A30"
baseRadius = "0.75rem"
font = "sans serif"

[theme.sidebar]
backgroundColor = "#18181C"
secondaryBackgroundColor = "#202025"
```

Manter o tema como ponto de partida global. Fazer refinamentos locais com CSS prefixado `qs-`; não alterar componentes gerais por meio de seletores excessivamente amplos.

### 3.2 Convenções de CSS

- Injetar CSS com `st.html("<style>…</style>")`.
- Toda classe própria começa com `qs-`.
- Preferir classes próprias em wrappers HTML simples e seletores `data-testid` do Streamlit somente quando necessário.
- Escopar seletores de `data-testid` a uma classe `qs-` próxima; testar após atualizar Streamlit.
- Não usar JavaScript, URLs de fontes externas, ícones externos ou frameworks de componentes.

| Classe | Regra visual e uso |
|---|---|
| `.qs-page` | Container de página; largura visual limitada, centralizada, padding lateral responsivo |
| `.qs-brand` | Marca alinhada ao centro na Home inicial |
| `.qs-brand-mark` | Marca de lupa/play em SVG local inline; tamanho recomendado 64×64 px na Home |
| `.qs-brand-title` | Nome da marca, peso 700, alto contraste |
| `.qs-brand-tagline` | Slogan em `text-secondary`, uma linha no desktop e até duas em celular |
| `.qs-search` | Wrapper da busca com fundo `surface`, borda `border`, raio `999px` |
| `.qs-search:focus-within` | Aplicar `focus-ring` e brilho vermelho suave; não remover o foco nativo sem substituto visível |
| `.qs-suggestions` | Agrupamento de exemplos de busca em linha no desktop, quebra em celular |
| `.qs-section` | Wrapper com margem vertical e separação clara de seção |
| `.qs-section-title` | Título de seção, alinhado à esquerda após os resultados aparecerem |
| `.qs-card` | Superfície `surface`, borda `border`, raio base, padding 16 px |
| `.qs-chip` | Base comum de chip; altura mínima 28 px, raio pill, alinhamento centrado |
| `.qs-chip--genre` | Fundo `genre-bg`, texto `genre-text`; sem efeito de botão |
| `.qs-chip--stream` | Cor da plataforma como fundo, texto com contraste AA; conteúdo textual |
| `.qs-chip--netflix` | Fundo `#B20710`, texto branco, borda `#FF8A82`; manter tipografia comum e sem brilho |
| `.qs-button-primary` | Ação principal vermelha com texto branco; hover `accent-hover` |
| `.qs-button-secondary` | Fundo transparente/`surface`, borda clara, texto `text-primary` |
| `.qs-button-tertiary` | Botão textual, sem fundo; usar para ações menos frequentes |
| `.qs-empty` | Painel vazio centralizado, ícone Material Symbols, título, explicação e uma ação |
| `.qs-alert` | Caixa de mensagem com ícone, texto e variação semântica success/warning/error |
| `.qs-rank` | Linha ou cartão de ranking com posição destacada e dados de afinidade |
| `.qs-price` | Preço em destaque e período/unidade legíveis |
| `.qs-price-meta` | Data de conferência e observação em texto secundário acessível |
| `.qs-divider` | Separador sutil `border`; não criar excesso de linhas decorativas |
| `.qs-mobile-stack` | Aplica espaçamento vertical quando colunas do desktop empilham no celular |
| `.qs-visually-hidden` | Texto acessível para leitor de tela quando um ícone isolado não puder ser evitado |

Exemplo de ícones com Material Symbols: `:material/search:`, `:material/favorite:`, `:material/bookmark:`, `:material/play_arrow:`, `:material/arrow_forward:`. Usar ícone junto a texto quando a ação não for universalmente óbvia.

## 4. Componentes

### 4.1 Barra de busca

**Anatomia:** ícone de lupa; campo de texto; botão de limpar opcional; botão de buscar opcional se a busca não atualizar ao enviar. Um único controle deve parecer a barra, sem criar dois botões concorrentes.

**Streamlit:** `st.text_input` com ícone e, se necessário, `st.button` dentro de `st.columns`; envolver visualmente com container/classe de busca.

**Estados:**

- **Normal:** pílula com fundo `surface`, placeholder curto e ícone.
- **Hover:** borda um pouco mais clara, sem animação chamativa.
- **Foco/ativo:** anel `focus-ring` visível; cursor e texto legíveis.
- **Desabilitado:** contraste ainda legível, aparência não interativa.
- **Vazio:** placeholder orienta a ação; a lista de sugestões aparece abaixo, não dentro do campo.

### 4.2 Chips

**Gênero:** informativo e neutro; não clicável no escopo atual.  
**Streaming:** identificação textual colorida, não clicável, salvo se futuramente houver filtro.

**Streamlit:** HTML simples por `st.html` para renderização consistente de conjuntos de chips. Se um chip for interativo no futuro, usar `st.button`/controle nativo e representar visualmente o estado selecionado.

**Estados:**

- **Normal:** gênero em `genre-bg`; streaming com cor semântica e texto acessível.
- **Hover:** somente chips que sejam controles interativos; os demais não mudam.
- **Ativo/selecionado:** borda ou marca de seleção além da cor.
- **Desabilitado:** texto e contorno reduzidos, sem depender só de opacidade.
- **Vazio:** omitir grupo sem dados; não exibir “—” como chip.

### 4.3 Card de filme

**Anatomia:** título e ano; gêneros; rótulo “Onde assistir”; chips de serviços; ação à direita. Sem poster obrigatório: não deixar lacuna se não houver imagem.

**Streamlit:** `st.container(border=True)`, `st.columns`, `st.subheader`, `st.caption`, `st.button`; chips em `st.html`.

**Estados:**

- **Normal:** título em primeiro plano; metadados secundários; ação no fim.
- **Hover:** elevar discretamente a superfície se for clicável; não fazer todo o card parecer link quando só o botão é acionável.
- **Ativo:** botão indica “Favorito” ou “Favorito ✓”; manter rótulo e ícone alinhados.
- **Desabilitado:** ação indisponível com explicação curta.
- **Sem disponibilidade informada:** substituir chips por “Disponibilidade não informada” em legenda; não sugerir que o serviço não tem o título.

### 4.4 Botões

| Tipo | Aparência | Usar para |
|---|---|---|
| Primário | Fundo vermelho, texto branco, peso 600 | Ação principal da tela: “Buscar”, “Recomendar”, “Salvar” |
| Secundário | Fundo de superfície ou transparente, borda visível | Ação importante concorrente: “Limpar filtros”, “Ver detalhes” |
| Terciário | Texto ou ícone + texto sem caixa proeminente | Ação de baixo risco: “Remover”, “Voltar”, “Limpar” |

**Streamlit:** `st.button`, com CSS escopado. Não estilizar todo botão como primário; definir tipo e hierarquia intencionalmente.

**Estados:**

- **Normal:** rótulo verbal, área clicável confortável e contraste AA.
- **Hover:** variação de fundo/borda e cursor; sem mover layout.
- **Ativo/pressionado:** tonalidade mais escura, sem desaparecer.
- **Desabilitado:** visualmente inativo e com motivo visível quando a indisponibilidade for importante.
- **Aguardando resultado:** mudar o rótulo se aplicável (“Recomendando…”), usar `st.spinner` para processamento demorado e evitar múltiplos envios.

### 4.5 Estado vazio

**Anatomia:** ícone; título específico; explicação curta; uma ação principal.  
**Streamlit:** `st.container(border=True)`, `st.markdown` ou `st.subheader`, `st.caption`, `st.button`, ícone Material.

**Estados:**

- **Normal/vazio:** texto orienta como começar; exemplo: “Você ainda não favoritou nenhum filme.”
- **Hover:** aplica-se apenas à ação.
- **Ativo:** após clique, encaminha para busca ou ação correspondente.
- **Desabilitado:** a ação mostra o que falta para prosseguir.
- **Com dados:** estado vazio deixa de renderizar quando a lista tiver itens.

### 4.6 Alertas

**Anatomia:** ícone semântico, mensagem direta e detalhe/ação opcional.  
**Streamlit:** `st.success`, `st.info`, `st.warning`, `st.error`; manter o conteúdo textual e usar variações de cor apenas como reforço.

**Estados:**

- **Normal:** exibe mensagem completa em uma linha ou bloco curto.
- **Hover:** sem interação quando informativo.
- **Ativo:** alerta acionável usa botão separado, não uma caixa inteira com aparência clicável.
- **Desabilitado:** não aplicável a mensagens passivas; ação associada pode estar desabilitada.
- **Sem dados:** não renderizar alerta vazio.

### 4.7 Item de ranking de recomendação

**Anatomia:** posição numerada; nome do serviço; nota/afinidade com rótulo explicativo; favoritos disponíveis naquele serviço; resumo de planos; ação de ver/expandir detalhes se necessária.

**Streamlit:** `st.container(border=True)` e `st.columns`; `st.metric` pode ser usado para afinidade se a formatação não prejudicar a hierarquia; `st.expander` opcional para detalhes de planos.

**Estados:**

- **Normal:** posição + serviço + afinidade + títulos relacionados são visíveis; preço resumido aparece sem exigir interação.
- **Hover:** elevar sutilmente somente se houver ação no card.
- **Ativo/selecionado:** destacar com borda ou fundo alternativo, além de eventual seleção.
- **Desabilitado:** indisponibilidade de dados explicitada, sem fabricar nota ou plano.
- **Sem recomendações:** mostrar estado vazio com ação “Recomendar”; explicar que a lista depende dos favoritos.

### 4.8 Plano e preço

**Anatomia:** nome do plano; preço mensal; moeda explícita (`R$`); periodicidade; data em que o valor foi conferido; fonte ou ressalva se o dado tiver validade limitada. Não exibir selo de “melhor preço” sem regra definida.

**Streamlit:** `st.container(border=True)` ou linhas em `st.columns`; `st.caption` para conferência. Para comparar vários serviços/plano, preferir cartões responsivos a uma tabela larga em celular.

**Estados:**

- **Normal:** preço em destaque; periodicidade junto ao valor.
- **Hover:** sem efeito se for apenas informativo.
- **Ativo/selecionado:** borda ou indicador para plano selecionado na futura comparação.
- **Desabilitado:** plano indisponível com status escrito.
- **Sem preço confirmado:** “Preço não informado” e sem exibir preço antigo como atual. A data de conferência não deve ser omitida quando um valor é apresentado.

## 5. Layout por tela

### 5.1 Home / Buscar

**Desktop, estado inicial**

```text
┌──────────────────────────────────────────────────────────────┐
│                    [lupa + play]                              │
│               Streaming Recommendation                       │
│         Encontre onde seus favoritos combinam                │
│                                                              │
│     [ 🔍  Busque um filme ou série...              ]         │
│     Experimente: Matrix · Cidade de Deus · Duna              │
│                                                              │
│                    Como funciona                             │
│       1. Busque       2. Favorite       3. Descubra           │
│       encontre        marque seus      compare serviços       │
│       títulos         títulos          e planos               │
└──────────────────────────────────────────────────────────────┘
```

Hierarquia: marca → slogan → busca → sugestões → explicação do sistema em três passos. Centralizar apenas o bloco inicial, mantendo o conteúdo informativo bem legível.

**Desktop, após buscar**

```text
┌──────────────────────────────────────────────────────────────┐
│ [marca compacta]                    [Minhas listas] [Recom.] │
│ [ 🔍 termo pesquisado                              ]         │
│ Resultados para “...”                                        │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Título (ano)                 [Favoritar]                 │ │
│ │ gêneros                                                   │ │
│ │ Onde assistir  [serviço] [serviço]                        │ │
│ └──────────────────────────────────────────────────────────┘ │
│                 ...                                          │
└──────────────────────────────────────────────────────────────┘
```

Encolher o cabeçalho sem remover a busca. O resultado da consulta deve ser evidente. Se não houver correspondência, mostrar texto que confirme o termo buscado e a ação de tentar outra busca.

**Celular, estado inicial e resultados**

```text
┌────────────────────────────┐
│        [lupa + play]       │
│ Streaming                 │
│ Recommendation            │
│ Encontre onde seus        │
│ favoritos combinam        │
│ [ 🔍 Busque um título... ] │
│ Experimente: Matrix       │
│ Cidade de Deus · Duna     │
│                            │
│ Como funciona              │
│ 1. Busque                  │
│ 2. Favorite                │
│ 3. Descubra                │
└────────────────────────────┘
```

```text
┌────────────────────────────┐
│ [marca compacta]           │
│ [ 🔍 termo pesquisado  ]   │
│ Resultados                 │
│ ┌────────────────────────┐ │
│ │ Título (ano)           │ │
│ │ gêneros                │ │
│ │ Onde assistir          │ │
│ │ [serviço] [serviço]    │ │
│ │ [♡ Favoritar]          │ │
│ └────────────────────────┘ │
└────────────────────────────┘
```

Empilhar conteúdo; manter busca e ação no alcance; permitir quebra de linha em gêneros e serviços. Evitar colunas lado a lado no card em telas estreitas.

### 5.2 Card de filme

```text
┌──────────────────────────────────────────────┐
│ Título do filme (2024)          [♡ Favoritar]│
│ [Drama] [Ficção científica]                  │
│ Onde assistir                                │
│ [Serviço A] [Serviço B]                      │
└──────────────────────────────────────────────┘
```

Em celular, botão fica abaixo do título ou em largura total, sem espremer título e ação na mesma linha.

### 5.3 Minhas listas

**Desktop**

```text
┌──────────────────────────────────────────────────────────────┐
│ Minhas listas     [Favoritos] [Watchlist — Sprint 3]        │
│ Filmes salvos para consultar depois                          │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Card de filme                                      ...   │ │
│ └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

```text
┌──────────────────────────────────────────────┐
│                 [material:favorite_border]   │
│             Sua lista está vazia             │
│      Busque um título e favorite-o para      │
│          encontrá-lo aqui depois.            │
│                  [Buscar filmes]             │
└──────────────────────────────────────────────┘
```

**Celular**

```text
┌────────────────────────────┐
│ Minhas listas              │
│ [Favoritos] [Watchlist]     │
│ ┌────────────────────────┐ │
│ │ Título (ano)           │ │
│ │ gêneros                │ │
│ │ serviços               │ │
│ │ [Remover]              │ │
│ └────────────────────────┘ │
└────────────────────────────┘
```

Na tela vazia, usar o mesmo padrão empilhado, texto centralizado e botão de largura confortável. Se watchlist ainda não estiver implementada, não apresentar uma aba que pareça funcional.

### 5.4 Recomendações

**Desktop**

```text
┌──────────────────────────────────────────────────────────────┐
│ Recomendações                                                │
│ Compare os serviços com base nos filmes que você favoritou.  │
│                             [Recomendar]                     │
│                                                              │
│  1  Serviço A                   Afinidade 86%                │
│     Seus favoritos neste serviço: Filme X, Filme Y           │
│     Planos                                                   │
│     Básico — R$ 00,00/mês · conferido em DD/MM/AAAA          │
│  ──────────────────────────────────────────────────────────  │
│  2  Serviço B                   Afinidade 72%                │
│     Seus favoritos neste serviço: Filme Z                    │
│     Padrão — R$ 00,00/mês · conferido em DD/MM/AAAA          │
└──────────────────────────────────────────────────────────────┘
```

**Celular**

```text
┌────────────────────────────┐
│ Recomendações              │
│ Baseadas nos seus favoritos│
│ [Recomendar]               │
│ ┌────────────────────────┐ │
│ │ #1 · Serviço A         │ │
│ │ Afinidade: 86%         │ │
│ │ Favoritos: Filme X, Y  │ │
│ │ Plano Básico           │ │
│ │ R$ 00,00/mês           │ │
│ │ Conferido DD/MM/AAAA   │ │
│ └────────────────────────┘ │
│ ┌────────────────────────┐ │
│ │ #2 · Serviço B         │ │
│ │ ...                    │ │
│ └────────────────────────┘ │
└────────────────────────────┘
```

Exibir ranking em ordem decrescente conforme regra de afinidade definida pelo produto. Não sugerir precisão científica: mostrar rótulo claro para “afinidade” e como a nota é calculada, quando essa lógica estiver definida. Não inventar nota, cobertura de títulos, plano ou preço. Se o usuário não tiver favoritos, orientar a adicionar filmes antes de recomendar.

### 5.5 Login/cadastro futuro

**Desktop**

```text
┌──────────────────────────────────────────────────────────────┐
│ [marca]                                                      │
│                       Criar conta                            │
│                [E-mail                       ]               │
│                [Senha                        ]               │
│                [Continuar                    ]               │
│                Já tem conta? Entrar                          │
└──────────────────────────────────────────────────────────────┘
```

**Celular**

```text
┌────────────────────────────┐
│ [marca]                    │
│ Criar conta                │
│ [E-mail]                   │
│ [Senha]                    │
│ [Continuar]                │
│ Já tem conta? Entrar       │
└────────────────────────────┘
```

Manter formulário curto; mensagens de validação próximas do campo. Políticas de senha, privacidade e recuperação de acesso estão em aberto e não devem ser presumidas neste guia.

### 5.6 Detalhes do filme futuro

**Desktop**

```text
┌──────────────────────────────────────────────────────────────┐
│ ← Voltar                                                     │
│ Título (ano)                                  [Favoritar]    │
│ Gêneros                                                      │
│ Onde assistir: [serviço] [serviço]                           │
│ Sinopse / detalhes                                           │
└──────────────────────────────────────────────────────────────┘
```

**Celular**

```text
┌────────────────────────────┐
│ ← Voltar                   │
│ Título (ano)               │
│ gêneros                    │
│ Onde assistir              │
│ [serviço] [serviço]        │
│ [Favoritar]                │
│ Sinopse / detalhes         │
└────────────────────────────┘
```

Se não houver sinopse ou outros metadados, omitir a seção em vez de preencher com texto genérico.

## 6. Tom de voz e microtextos

### Voz

- Direta, amigável e útil.
- Escrever em português brasileiro; preferir verbos concretos.
- Não prometer que uma recomendação é “a melhor” sem critério verificável.
- Explicar incerteza dos dados com clareza, sem alarmismo.

### Exemplos

| Contexto | Texto |
|---|---|
| Slogan | “Descubra qual streaming combina com seus favoritos.” |
| Busca | “Busque um filme ou série” |
| Sugestões | “Experimente: Matrix, Cidade de Deus, Duna” |
| Como funciona | “Busque. Favorite. Compare os serviços que combinam com você.” |
| Ação de busca | “Buscar” |
| Favoritar | “Favoritar” |
| Já favoritado | “Favorito” |
| Remover da lista | “Remover” |
| Recomendar | “Recomendar serviços” |
| Estado vazio de favoritos | “Sua lista está vazia. Busque um título e favorite-o para encontrá-lo aqui depois.” |
| Estado vazio da watchlist | “Você ainda não salvou títulos para assistir depois.” |
| Estado vazio de recomendação | “Adicione alguns favoritos para descobrir quais serviços combinam com você.” |
| Busca sem resultados | “Não encontramos títulos para essa busca. Tente outro nome.” |
| Erro na busca | “Não foi possível carregar os resultados agora. Tente novamente.” |
| Erro ao recomendar | “Não foi possível gerar recomendações agora. Seus favoritos continuam salvos.” |
| Preço ausente | “Preço não informado.” |
| Data do preço | “Preço conferido em DD/MM/AAAA.” |
| Afinidade | “Afinidade estimada com seus favoritos” |
| Ação para estado vazio | “Buscar filmes” |
| Navegação | “Buscar”, “Minhas listas”, “Recomendações” |

Não inserir exemplos fictícios de preços ou afinidades na interface real. Os valores de exemplo nos wireframes são apenas marcadores visuais, não conteúdo de produção.

> **Nota de implementação:** enquanto a busca cobrir só filmes (decisão em aberto nº 5), o placeholder diz “Busque um filme, ex.: Matrix”. Os exemplos ficam no próprio placeholder, sem a linha “Experimente:” com botões, e usam apenas títulos que existem no catálogo.

## 7. O que não fazer

- Não copiar identidade, layout, marca, logotipos ou tipografia de Netflix ou de qualquer serviço de streaming.
- Não usar a cor primária e a cor da etiqueta Netflix como se fossem a mesma coisa: distinguir etiqueta e ação por borda, formato e tratamento visual.
- Não criar carrossel, banner promocional ou pôster grande que concorra com a busca em destaque.
- Não depender apenas da cor para comunicar seleção, erro, disponibilidade ou posição no ranking.
- Não usar texto cinza com contraste insuficiente em legendas importantes.
- Não tratar chip informativo como botão; não fazer o card inteiro parecer clicável se só existe uma ação.
- Não inventar catálogo, disponibilidade por serviço, nota de afinidade, preço ou data de conferência.
- Não mostrar preço sem periodicidade nem omitir a data em que foi conferido.
- Não esconder erros ou listas vazias; oferecer mensagem e próximo passo.
- Não usar JavaScript, CSS que dependa de estrutura interna frágil, fontes que exijam build ou bibliotecas externas.
- Não usar emojis como substituto do sistema de ícones; preferir Material Symbols.
- Não apertar texto e controles em colunas no celular; empilhar e deixar chips quebrarem linha.
- Não marcar futuramente watchlist, login, comparação ou filtros como disponíveis antes de essas funções existirem.

## 8. Checklist antes do PR

- [ ] A busca é a ação mais evidente na Home e continua acessível após os resultados.
- [ ] A hierarquia da tela funciona em desktop e celular; nenhum controle foi espremido.
- [ ] Todos os componentes usam os tokens e classes `qs-*`; não há estilos genéricos acidentais.
- [ ] Texto, foco, erro e seleção permanecem compreensíveis sem depender somente da cor.
- [ ] Pares de texto e fundo atendem WCAG AA; cores de serviços foram verificadas individualmente.
- [ ] Ações têm rótulos claros e estados normal, hover, ativo e desabilitado.
- [ ] Estados vazios, sem resultado e de erro indicam um próximo passo.
- [ ] Preço tem moeda, periodicidade e data de conferência; dado desconhecido não foi inventado.
- [ ] O ranking e a afinidade são apresentados sem sugerir critérios ainda não definidos.
- [ ] Nenhum elemento imita visualmente Netflix ou outro serviço.
- [ ] A tela usa componentes disponíveis no Streamlit 1.67, sem JavaScript ou dependências externas.

## 9. Decisões em aberto

1. Qual é a regra exata de cálculo da nota/afinidade e como desempatar serviços?
2. Quais são as fontes de dados para preços e disponibilidade, com que frequência serão atualizadas e como a interface indicará divergência?
3. Os dados de preço incluem promoções, impostos, período introdutório, anúncios ou compartilhamento de plano?
4. Quais limites existem para quantidade de favoritos e de itens em watchlist?
5. A busca abrange filmes e séries ou somente filmes no primeiro escopo implementado?
6. O que acontece ao clicar num serviço ou num título: abrir detalhe interno, link externo ou apenas exibir informação?
7. Qual é o mecanismo de persistência das listas e, futuramente, autenticação?
8. Quais são as regras de validação, recuperação de senha e privacidade para login/cadastro?
9. A nota será exibida como percentual, escala ou categoria (por exemplo, “Alta afinidade”)? Definir uma forma consistente antes do lançamento.

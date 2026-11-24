# Streaming Recommendation

**Streaming Recommendation** é uma aplicação web que ajuda o usuário a escolher em qual serviço de streaming vale a pena assinar. A partir dos filmes que ele já assistiu e dos que deseja assistir, o sistema indica as plataformas mais adequadas ao seu gosto e apresenta os planos e valores de cada uma.

## Repositório

O código-fonte do projeto está disponível no GitHub: [Bigodeiro/streaming_reccomendation](https://github.com/Bigodeiro/streaming_reccomendation)

## Ideia geral do projeto

Hoje existem muitos serviços de streaming, cada um com um catálogo e vários planos de preço. Escolher qual assinar costuma ser difícil e caro.

A ideia do projeto é resolver isso a partir do gosto do próprio usuário: ele marca os filmes que **já viu** e os que **quer ver**, e o sistema indica **quais streamings valem mais a pena** para ele, mostrando também os **planos disponíveis** de cada um.

## Descrição geral do sistema

O sistema é uma página web em que o usuário:

1. Cria uma conta e faz login.
2. Marca filmes como **favoritos** (já viu e gostou) ou adiciona à **watchlist** (quer ver).
3. Recebe recomendações de streaming com base nesses dois grupos de filmes.
4. Consulta, para cada streaming recomendado, os planos e preços disponíveis.

### Funcionalidades (histórias de usuário)

| Código | Funcionalidade | Prioridade |
|--------|----------------|------------|
| H1 | Autenticação de usuário (cadastro e login) | Média |
| H2 | Marcar mídia como favorita | Alta |
| H3 | Recomendação com base nos favoritos | Alta |
| H4 | Marcar mídia para a watchlist | Alta |
| H5 | Recomendação com base na watchlist | Média |
| H6 | Buscar filmes por título | Alta |
| H7 | Ver planos e preços dos streamings recomendados | Alta |
| H8 | Ver minhas listas (favoritos e watchlist) | Média |
| H9 | Remover filme dos favoritos ou da watchlist | Média |
| H10 | Ver detalhes de um filme | Média |
| H11 | Administrador: cadastrar e atualizar streamings e planos | Média |
| H12 | Filtrar recomendações por faixa de preço | Baixa |
| H13 | Comparar planos de streamings | Baixa |
| H14 | Editar perfil e recuperar senha | Baixa |

## Tecnologias

| Camada | Tecnologia |
|--------|------------|
| Front-end | Streamlit |
| Back-end | Python (lógica de negócio e acesso a dados) |
| Banco de dados | SQLite3 |
| Fonte de dados dos filmes/streamings | Streaming Availability API v4 (`scripts/atualizar_catalogo.py`) |
| Execução | Local inicialmente |

## Catálogo de filmes e streamings

O catálogo usado pela aplicação fica em `fontes/filmes_local.json`. Cada filme traz `titulo`, `ano`, `generos`, `streamings` (somente serviços de assinatura disponíveis no Brasil) e os ids `imdb_id`/`tmdb_id` usados para casar registros entre atualizações:

```json
{
  "atualizado_em": "2026-11-24",
  "fonte": "Streaming Availability API v4",
  "pais": "br",
  "filmes": [
    {
      "id": 1,
      "titulo": "The Godfather",
      "ano": 1972,
      "generos": ["Crime", "Drama"],
      "streamings": ["Paramount+"],
      "imdb_id": "tt0068646",
      "tmdb_id": "movie/238"
    }
  ]
}
```

A fonte expõe os gêneros em `Filme.generos` e a disponibilidade em `streamings_do_filme(id)` (`onde_assistir` ficou como alias). Os nomes dos streamings passam pelo mapa em `fontes/streamings.py`, que usa os ids da API (`netflix`, `prime`, `hbo`, `disney`, `apple`, `paramount`, ...). Esse mesmo mapa deve ser usado como `slug` na tabela `streamings` da H3.1; serviços fora dele, como Globoplay, são descartados na importação.

### API escolhida

Usamos a [Streaming Availability API](https://docs.movieofthenight.com/) (Movie of the Night) porque é a única opção consultada que entrega, em uma chamada, gêneros, ano, ids externos e **onde assistir no Brasil**, com 1.000 requisições gratuitas por mês, uso comercial permitido e cache local permitido. JustWatch não oferece API self-service; TMDB e OMDb não trazem disponibilidade. A API não localiza em português, então títulos e gêneros do catálogo ficam em inglês.

### Atualizando o catálogo

1. Obtenha uma chave gratuita em [developers.movieofthenight.com](https://developers.movieofthenight.com/).
2. Defina `STREAMING_AVAILABILITY_API_KEY` no ambiente (ou em `.env`, que já é ignorado pelo Git).
3. Edite `scripts/titulos_para_buscar.txt` com os filmes desejados (um por linha).
4. Rode:

```bash
python -m scripts.atualizar_catalogo --dry-run   # confere o JSON sem gravar
python -m scripts.atualizar_catalogo             # grava fontes/filmes_local.json
```

O script consulta `/shows/search/title` com `country=br` e `show_type=movie`, aproveita apenas opções `subscription`, normaliza os serviços pelo mapa canônico e grava o arquivo por completo de forma atômica. Não é preciso rodá-lo para usar ou testar o app: a suíte de testes usa payloads mockados e não faz chamadas de rede.

### Varredura geral e retomada da base

Para popular a base aos poucos, **sem escrever uma lista de filmes**, use:

```bash
python -m scripts.construcao_inicial --status           # mostra o progresso
python -m scripts.construcao_inicial                    # varre até acabar a cota
python -m scripts.construcao_inicial --max-paginas 5    # limita páginas nesta execução
python -m scripts.construcao_inicial --max-novos 20     # limita filmes novos
python -m scripts.construcao_inicial --todos-catalogos  # inclui aluguel/compra/outros
python -m scripts.construcao_inicial --reiniciar-progresso
```

Ele consulta `/shows/search/filters?country=br&show_type=movie`, que devolve o catálogo inteiro em páginas de 20 filmes — não precisa de `scripts/titulos_para_buscar.txt`. Por padrão a varredura usa `netflix.subscription,prime.subscription,hbo.subscription,disney.subscription,apple.subscription,paramount.subscription,crunchyroll.subscription,mubi.subscription` (derive de `fontes/streamings.py`), evitando filmes que só estão em aluguel/compra ou em serviços fora do mapa canônico. Use `--catalogos` para trocar essa lista ou `--todos-catalogos` para varrer tudo o que a API oferece no país.

O cursor da paginação fica em `scripts/progresso_construcao.json` (ignorado pelo Git). Quando a API responder que a cota/tokens acabaram (HTTP 429, 402 ou mensagem de quota/limite), ele salva o cursor atual e encerra sem erro; na próxima execução continua exatamente da página seguinte. Se o processo cair por outro motivo, o que já foi adicionado também continua salvo.

Filmes com o mesmo `imdb_id`, `tmdb_id` ou `título + ano` são ignorados, inclusive quando aparecem de novo em uma página retomada. Assim rodar o script várias vezes não cria mídias repetidas nem muda os ids dos favoritos. `--dry-run` consulta a API e mostra o resumo sem gravar nada.

## Equipe

Jouberth, Cauã, João Pedro, Enzo

## Quadro Kanban

O acompanhamento das tarefas é feito no quadro Kanban do projeto:

**[Kanban - Streaming Recommendation](https://github.com/users/Bigodeiro/projects/1)**.

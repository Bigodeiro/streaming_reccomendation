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

| Código | Funcionalidade |
|--------|----------------|
| H1 | Autenticação de usuário |
| H2 | Marcar mídia como favorita [Sprint1] |
| H3 | Recomendação com base nos favoritos |
| H4 | Marcar mídia para a watchlist |
| H5 | Gerar recomendação com base na watchlist |

## Tecnologias

| Camada | Tecnologia |
|--------|------------|
| Front-end | Streamlit |
| Back-end | Python (lógica de negócio e acesso a dados) |
| Banco de dados | SQLite3 |
| Fonte de dados dos filmes/streamings | A definir |
| Execução | Local inicialmente |

## Equipe

Jouberth, Cauã, João Pedro, Enzo

## Quadro Kanban

O acompanhamento das tarefas é feito no quadro Kanban do projeto:

**[Kanban - Streaming Recommendation](https://github.com/users/Bigodeiro/projects/1)**.

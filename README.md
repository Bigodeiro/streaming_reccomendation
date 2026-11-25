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

### Como a recomendação funciona

A recomendação é **baseada em conteúdo** e serve como **apoio à decisão**: ela não promete que o usuário vai gostar de um serviço, apenas mostra onde há mais títulos parecidos com os que ele já escolheu e quanto custa assinar.

Na versão atual, com base nos favoritos, o sistema:

1. Exige pelo menos 3 filmes favoritos.
2. Descobre o gênero que mais se repete entre eles.
3. Conta, em cada streaming, quantos filmes desse gênero estão disponíveis.
4. Monta um ranking, do serviço com mais filmes para o com menos, e mostra os planos e preços de cada um.

Não usamos filtragem colaborativa (comparar usuários entre si), porque o projeto não tem uma base de usuários e avaliações para isso. Os detalhes estão em [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md).

### Estado atual

O projeto é desenvolvido em sprints de duas semanas (planejamento em [`docs/sprints.md`](docs/sprints.md)).

- **Sprint 1:** busca de filmes por título, favoritos e lista de favoritos.
- **Sprint 2 (em andamento):** recomendação com base nos favoritos e planos e preços dos streamings.
- **Sprint 3:** cadastro e login, watchlist e recomendação com base nela.
- **Sprint 4:** testes, correções e apresentação.

Enquanto a autenticação não chega, o sistema usa um perfil de demonstração.

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
| Back-end | Python (lógica de negócio e acesso a dados), com os padrões Handle/Body e Factory |
| Banco de dados | SQLite3 |
| Fonte de dados dos filmes | Catálogo local em JSON (`fontes/filmes_local.json`), gerado a partir da Streaming Availability API |
| Fonte de dados dos planos e preços | Dados fixos cadastrados no banco, conferidos nos sites oficiais de cada streaming |
| Testes | pytest |
| Execução | Local inicialmente |

### Fonte de dados

Os filmes, com seus gêneros e os streamings em que estão disponíveis no Brasil, vêm de um **catálogo local em JSON**. Ele é gerado pelo script `scripts/atualizar_catalogo.py`, que consulta a Streaming Availability API. Assim, o app abre rápido e funciona sem internet e sem chave de API.

Os **planos e preços** são dados fixos, carregados no banco ao iniciar o app. Cada preço guarda a data em que foi conferido no site do streaming, porque esses valores mudam com frequência. Os preços considerados são os mensais, sem promoções.

## Como rodar

```bash
python -m venv .venv
source .venv/bin/activate          # no Windows (PowerShell): .venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Para rodar os testes:

```bash
python -m pytest -q
```

## Documentação

- [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md): estrutura do código, padrões de projeto e critério de recomendação
- [`docs/sprints.md`](docs/sprints.md): planejamento das sprints
- [`docs/DESIGN.md`](docs/DESIGN.md): documento de design da interface

## Equipe

Jouberth, Cauã, João Pedro, Enzo

## Quadro Kanban

O acompanhamento das tarefas é feito no quadro Kanban do projeto:

**[Kanban - Streaming Recommendation](https://github.com/users/Bigodeiro/projects/1)**.

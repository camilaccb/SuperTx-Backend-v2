# SuperTx
Projeto backend da sprint de **Arquitetura de software** do [curso de pós graduação de Engenharia de Sofware da PUC Rio](https://especializacao.ccec.puc-rio.br/especializacao/engenharia-de-software). As principais tecnologias que serão utilizadas aqui é são:

- Flask
- SQLAlchemy
- OpenAPI3
- SQLite
- Serviço de autenticação (Authlib)

## Objetivo do projeto
Sistema web que possibilita o gerencialmento do corridas de taxi. Permite o cadastro, a visualização,atualização e deleção de corridas. Caso queira entender um pouco mais da motivaçao do projeto, veja esse [documento](https://github.com/camilaccb/BuddyConnect-Backend/blob/main/motivacao-projeto.md).

## Arquitetura do projeto
O projeto é composto por 3 componentes que se comunicam seguindo o padrão REST. Um desses componentes é um serviço externo responsável pela autenticação do usuário. A persistência dos dados do componente do backend é feita utilizando o SQLite. Cada um dos componentes desenvolvidos pode ser executado utilizando container.

![alt text](<Diagrama arquitetura supertx.drawio.png>)


## Como executar o servidor 
Para executar o projeto, siga os passos:
1. Clone o repositório
2. Instale a lib do poetry usando o pip
```bash
pip install poetry
```

> É fortemente indicado o uso de ambientes virtuais do poetry, pois segue a orientação prevista na [PEP 621](https://peps.python.org/pep-0621/) 
3. Faça a instalação das dependências listadas no [arquivo pyproject.toml](https://github.com/camilaccb/BuddyConnect-Backend/blob/main/pyproject.toml):

```bash
poetry install
```
4. Ative o ambiente virtual. Caso tenha alguma dúvida consultar a seguinte [documentação](https://python-poetry.org/docs/basic-usage/#:~:text=shell%0Awhich%20python-,Activating%20the%20virtual%20environment,-The%20easiest%20way)

```bash
poetry shell
```

5. Execute a API

```bash
(env)$ flask run --host 0.0.0.0 --port 5000
```

## Como executar através do docker

TBD




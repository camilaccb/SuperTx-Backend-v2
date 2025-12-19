# SuperTx
Projeto backend da sprint de **Arquitetura de software** do [curso de pós graduação de Engenharia de Sofware da PUC Rio](https://especializacao.ccec.puc-rio.br/especializacao/engenharia-de-software). As principais tecnologias que serão utilizadas aqui é são:

- Flask
- SQLAlchemy
- OpenAPI3
- SQLite


## Objetivo do projeto
Sistema web que possibilita o gerencialmento do corridas de taxi. Permite o cadastro, a visualização,atualização e deleção de corridas e clientes. Caso queira entender um pouco mais da motivaçao do projeto, veja esse [documento](https://github.com/camilaccb/SuperTx-Backend-v2/blob/main/motivacao-projeto.md). É uma evolução do projeto da disciplina de fullstack, considerando integração com componentes externos e conteinerização.

## Arquitetura do projeto
O projeto é composto por uma interface (frontend) e um módulo API (backend) que consulta 2 serviços externos. Os componentes se comunicam seguindo o padrão REST. A persistência dos dados do componente do backend é feita utilizando o SQLite. Cada um dos componentes desenvolvidos pode ser executado utilizando container.

![alt text](<Diagrama-arquitetura.png>)

### Integrações / APIs Externas

O projeto se integra com algumas APIs externas para funcionalidades de geolocalização, roteamento e preços de combustíveis. Abaixo estão as integrações utilizadas atualmente e notas de configuração.

- **OpenRouteService** (Geocodificação e Roteamento)
	- **Propósito**: Obter coordenadas (lon, lat) a partir de endereços e calcular rotas/distâncias estimadas (usado em `Corridas.geocodificar_endereco` e `Corridas.obter_distancia`).
	- **Docs**: https://openrouteservice.org/dev/#/api-docs
	- **Autenticação**: Requer chave de API (token).
	- **Gerenciamento de credenciais via Docker Secrets**:
		- O token de autenticação é armazenado em um arquivo (secret) gerenciado pelo Docker.
		- A variável de ambiente `ROUTING_API_KEY_FILE` contém o caminho para esse arquivo dentro do container.
		- O backend lê o conteúdo do arquivo apontado por `ROUTING_API_KEY_FILE` para obter a chave.
		- Isso garante que credenciais sensíveis não sejam expostas diretamente em variáveis de ambiente ou no código.
		- **Referência**: [Docker Secrets Documentation](https://docs.docker.com/engine/swarm/secrets/) | [Docker Compose Secrets](https://docs.docker.com/compose/use-secrets/)


- **CombustivelAPI** (Preços de combustíveis)
	- Propósito: Recuperar preços de combustível por estado para cálculo de custo por corrida (usado em `Corridas.obter_preco_combustivel`).
	- Docs: https://combustivelapi.com.br/
	- Observação: não é necessário chave para uso básico.



## Como executar o servidor 
Para executar o projeto, siga os passos:
1. Clone o repositório
2. Instale a lib do poetry usando o pip
```bash
pip install poetry
```

> É fortemente indicado o uso de ambientes virtuais do poetry, pois segue a orientação prevista na [PEP 621](https://peps.python.org/pep-0621/) 
3. Faça a instalação das dependências listadas no [arquivo pyproject.toml](https://github.com/camilaccb/SuperTx-Backend-v2/blob/main/pyproject.toml):

```bash
poetry install
```
4. Recupere o comando para ativar o ambiente virtual e execute no terminal. Caso tenha alguma dúvida consultar a seguinte [documentação](https://python-poetry.org/docs/cli#env-activate:~:text=about%20these%20commands.-,env%20activate,-The%20env%20activate)

```bash
poetry env activate
```

5. Com o ambiente virtual ativado execute a API

```bash
(env)$ flask run --host 0.0.0.0 --port 5000
```

## Como executar através do docker

Certifique-se de ter o [Docker](https://docs.docker.com/engine/install/) instalado e em execução em sua máquina.

1. Navegue até o diretório que contém o Dockerfile e o pyproject.toml no terminal.

Execute **como administrador** o seguinte comando para construir a imagem Docker:

```
$ docker build -t super-tx-backend .
```

2. Uma vez criada a imagem, para executar o container basta executar, **como administrador**, seguinte o comando:

```
$ docker run -p 5000:5000 super-tx-backend
```

3. Uma vez executando, para acessar a API, basta abrir o [http://localhost:5000/#/](http://localhost:5000/#/) no navegador.



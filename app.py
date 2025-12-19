"""
API da aplicação que utiliza a lib flask-openapi3 para gerar a documentação automaticamente a partir do código

"""

from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from datetime import datetime, timedelta


from model import Session, Corridas, Clientes
from logger import logger
from schemas import *

from flask_cors import CORS

# Inclui metadados da API
info = Info(title="SuperTx API", version="2.0.0")
app = OpenAPI(__name__, info = info)

# Permite que outras origens realizem solicitações as rotas
CORS(app)


# Definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
corridas_tag = Tag(name="Corridas", description="Adição, visualização, atualização e deleção de uma corrida")
clientes_tag = Tag(name="Clientes", description="Adição, visualização, atualização e deleção de clientes")

# Rotas da API (endpoints, paths, views)
@app.get('/', tags=[home_tag])
def home():
   
    return redirect('/openapi')


@app.post('/corridas', tags=[corridas_tag],
          responses={"200": CorridaViewSchema , "409": ErrorSchema, "400": ErrorSchema})
def add_corrida(form: CorridaSchema):
    """
    Adiciona uma nova corrida na base

    Retorna uma representação da corrida inserida na base
    """
    
    id_cliente = form.id_cliente

    # Iniciando a sessão com o banco para adicionar a corrida
    session = Session()
    
    
    # Verifica se a corrida é de um cliente já cadastrado
    cliente = session.query(Clientes).filter_by(cpf_cliente = id_cliente).first() 

    # Retorna erro caso cliente não esteja cadastrado
    if not cliente:
        error_msg = "Cliente não cadastrado"
        logger.warning(error_msg)
        return {"mensagem": error_msg}, 409 
    

    corrida = Corridas(
    id_cliente = form.id_cliente,
    tipo_corrida = form.tipo_corrida,
    valor_corrida = form.valor_corrida,
    origem_corrida = form.origem_corrida,
    destino_corrida = form.destino_corrida
    )

    # Recuperando as coodernadas e o estado por meio do endereço
    
    corrida.estado_corrida, coordenadas_origem = corrida.geocodificar_endereco(corrida.origem_corrida)
    corrida.estado_corrida, coodernadas_destino = corrida.geocodificar_endereco(corrida.destino_corrida)


    # Calculando a distância por meio das coordenadas geográficas
    corrida.distancia_corrida = corrida.obter_distancia(coordenadas_origem,coodernadas_destino)

    # Recuperando o valor do combustível de acordo com a localização
    corrida.valor_gasolina = corrida.obter_preco_combustivel(corrida.estado_corrida)

    # Calculando valor líquido da corrida
    performance_carro_consumo = 0.125 #8km por litro de  combustível
    corrida.valor_liquido_corrida = corrida.valor_corrida - (corrida.valor_gasolina * corrida.distancia_corrida * performance_carro_consumo)

    try:
        # adicionando corrida
        session.add(corrida)
        # efetivando o camando de adição de novo item na tabela
        session.commit()
        logger.debug(f"Adicionado corrida")
        return apresenta_corrida(corrida), 200

    except IntegrityError as e:
        error_msg = "Corrida já salva na base"
        logger.warning(f"Corrida já adicionada")
        return {"mensagem": error_msg}, 409

    except Exception as e:
        #error_msg = "Não foi possível salvar nova corrida :/"
        error_msg = f"Não foi possível salvar nova corrida: {str(e)}"
        logger.warning(f"Erro ao adicionar corrida: {error_msg}")
        return {"mensagem": error_msg}, 400

@app.post('/clientes', tags=[clientes_tag],
          responses={"200": ClienteViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_cliente(form: ClienteSchema):
    """
    Adiciona uma novo cliente na base

    Retorna uma representação do cliente que foi cadastrado
    """

    cliente = Clientes(
    cpf_cliente = form.cpf_cliente,
    nome = form.nome,
    telefone = form.telefone
    )

    # Iniciando a sessão com o banco para adicionar o cliente
    session = Session()

    try:
        # adicionando cliente
        session.add(cliente)
        # efetivando o camando de adição de novo item na tabela de cliente
        session.commit()
        logger.debug(f"Adicionado cliente")
        return apresenta_cliente(cliente), 200

    except IntegrityError as e:
        error_msg = "Cliente já salvo na base"
        logger.warning(f"Corrida já cadastrado")
        return {"mensagem": error_msg}, 409

    except Exception as e:
        error_msg = "Não foi possível cadastrar o cliente :/"
        logger.warning(f"Erro ao cadastrar o cliente: {error_msg}")
        return {"mensagem": error_msg}, 400

@app.put('/clientes', tags=[clientes_tag],
        responses={"200": ClienteViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def update_cliente(form: ClienteSchema):
    """
    Atualiza um cliente existente na base

    Retorna o cliente cadastrado
    """
    cpf_cliente_atualizar = form.cpf_cliente
    print(cpf_cliente_atualizar)
    logger.debug(f"Atualizando dados do cliente com cpf: {cpf_cliente_atualizar}")

    nome_atualizar = form.nome
    telefone_atualizar = form.telefone

    # criando conexão com a base
    session = Session()

    try:
        # Buscar cliente
        cliente = session.query(Clientes).filter(
            Clientes.cpf_cliente == cpf_cliente_atualizar
        ).first()

        if not cliente:
            return {"mensagem": "Cliente não encontrado"}, 400

        # Atualizar campos
        cliente.nome = nome_atualizar
        cliente.telefone = telefone_atualizar
        cliente.ultima_atualizacao = datetime.now()

        # 3. Commit
        session.commit()

        # 4. Retornar cliente atualizado
        return apresenta_cliente(cliente), 200

    except Exception as e:
        logger.error(f"Erro ao atualizar cliente: {e}")
        return {"mensagem": "Erro ao atualizar cliente"}, 400

@app.delete('/clientes', tags=[clientes_tag],
            responses={"200": ClienteDelSchema, "409": ErrorSchema, "400": ErrorSchema})
def del_cliente(query: ClienteBuscaSchema):
    """Deleta um cliente a partir do cpf informado

    Retorna uma mensagem de confirmação da remoção.
    """
    cpf_cliente_deletar = query.cpf
    logger.debug(f"Deletando dados do cliente com cpf: {cpf_cliente_deletar}")
    
    # criando conexão com a base
    session = Session()
    
    # Verificando se o cliente possui corridas
    qtd_corridas = session.query(Corridas).filter(Corridas.id_cliente == cpf_cliente_deletar).count()

    # Retornar erro caso o cliente tenha corridas cadastradas
    if qtd_corridas:
        error_msg = "O cliente possui corridas associadas e não pode ser removido."
        logger.warning(f"Erro ao deletar cliente com cpf #{cpf_cliente_deletar}, {error_msg}")
        return {"mensagem": error_msg}, 409
    
    # fazendo a remoção
    count = session.query(Clientes).filter(Clientes.cpf_cliente == cpf_cliente_deletar).delete()
    session.commit()

    if count:
        # retorna a representação da mensagem de confirmação
        logger.debug(f"Deletado cliente com cpf #{cpf_cliente_deletar}")
        return {"mensagem": "Cliente removido", "cpf": cpf_cliente_deletar}
    else:
        # se o cliente não foi encontrado
        error_msg = "Cliente não encontrado na base :/"
        logger.warning(f"Erro ao deletar cliente com cpf #'{cpf_cliente_deletar}', {error_msg}")
        return {"mensagem": error_msg}, 400
    
@app.get('/corridas', tags=[corridas_tag],
        responses={"200": CorridaViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def recupera_corridas_recentes():
    """
    Retorna corridas
    """
    # criando conexão com a base
    session = Session()

    ultimo_mes = datetime.now() - timedelta(days=30)

    # Executa query
    resultado_corridas_recentes = session.query(Corridas) \
                                    .filter(Corridas.hora_registro_corrida >= ultimo_mes) \
                                    .order_by(Corridas.hora_registro_corrida.desc()) \
                                    .all()

    # Serializa cada objeto Corridas para um dicionário compatível com JSON
    corridas_serializadas = [apresenta_corrida(c) for c in resultado_corridas_recentes]

    return corridas_serializadas, 200

@app.get('/clientes', tags=[clientes_tag],
        responses={"200": ClienteViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def recupera_clientes():
    """
    Retorna corridas
    """
    # criando conexão com a base
    session = Session()

    ultimo_mes = datetime.now() - timedelta(days=30)

    # Executa query
    resultado_clientes_recentes = session.query(Clientes) \
                                    .filter(Clientes.ultima_atualizacao >= ultimo_mes) \
                                    .order_by(Clientes.ultima_atualizacao.desc()) \
                                    .all()

    # Serializa cada objeto Clientes para um dicionário compatível com JSON
    clientes_serializados = [apresenta_cliente(c) for c in resultado_clientes_recentes]

    return clientes_serializados, 200
   










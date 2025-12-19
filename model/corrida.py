"""
Cria a classe relativa a entidade de corrida que vai ser utilizada no banco de dados

"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from typing import Union, Optional, Tuple, List
import requests
import os

from model import Base


def _carregar_chave_api_rotas() -> Union[str, None]:
    """Carrega a chave da API de rotas a partir de arquivo apontado por
    `ROUTING_API_KEY_FILE` ou a partir da variável de ambiente `ROUTING_API_KEY`.
    Retorna a chave como string ou None caso não encontrada.
    """
    file_path = os.environ.get("ROUTING_API_KEY_FILE")
    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            pass

    return os.environ.get("ROUTING_API_KEY")


ROUTING_API_KEY = _carregar_chave_api_rotas()

# Cria a classe Corridas a partir da classe Base (utiliza o conceito de herança)
class Corridas(Base):
    __tablename__ = "corridas"

    id_corrida = Column(Integer, primary_key=True)
    id_cliente = Column(String(11), ForeignKey("clientes.cpf_cliente"))
    tipo_corrida = Column(String)
    valor_corrida = Column(Float)
    hora_registro_corrida = Column(DateTime, default=datetime.now())
    origem_corrida = Column(String)
    destino_corrida = Column(String)
    distancia_corrida = Column(Float)
    estado_corrida = Column(String)
    valor_liquido_corrida = Column(Float)
    valor_gasolina = Column(Float)

    clientes= relationship("Clientes",back_populates="corridas")


    def __init__(self, id_cliente: str,tipo_corrida: str, valor_corrida: float, origem_corrida: str, destino_corrida:str, hora_registo_corrida: Union[DateTime, None] = None):

        """
        Cria uma corrida

        Argumentos:
            cliente_id: id do cliente da corrida
            tipo_de_corrida: especifica se corrida foi na rua, por aplicativo ou contato direto do cliente
            valor_corrida: valor total em real da corrida
            hora_registro_corrida: dia e hora em que a corrida foi cadastrada no sistema
            origem_corrida: endereço de origem da corrida
            destino_corrida: endereço de destino da corrida

        """
        self.id_cliente = id_cliente
        self.tipo_corrida = tipo_corrida
        self.valor_corrida = valor_corrida
        self.origem_corrida = origem_corrida
        self.destino_corrida = destino_corrida
        self.hora_registro_corrida = hora_registo_corrida if hora_registo_corrida is not None else datetime.now()

        
    def geocodificar_endereco(self, endereco: str) -> Tuple[Optional[str], List[float]]:
        """Retorna a região (UF) e as coordenadas (longitude, latitude) para um endereço.

        Argumentos:
            endereco (str): Endereço completo ou parcial (ex.: 'Av. Paulista, 1000, SP').

        Retorna:
            tuple: (uf, coordenadas)
                - uf (str|None): Código da unidade federativa (ex.: 'SP', 'RJ') ou None se não disponível.
                - coordenadas (list[float]): Lista com longitude e latitude [lon, lat].
        """
        url = "https://api.openrouteservice.org/geocode/search"
        key = ROUTING_API_KEY
        if not key:
            raise RuntimeError("Chave da API de rotas não configurada. Defina a variável de ambiente `ROUTING_API_KEY_FILE` ou `ROUTING_API_KEY`.")

        params = {
            "api_key": key,
            "text": endereco
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if not data["features"]:
            raise ValueError(f"Endereço não encontrado: {endereco}")

        feature = data["features"][0]
        props = feature["properties"]

        region = props.get("region_a")  # ex.: "CE"
        coordinates = feature["geometry"]["coordinates"]  # [lon, lat]

        return region, coordinates


    def obter_distancia(self, coord_origem: Union[list, tuple], coord_destino: Union[list, tuple]) -> float:
        """Calcula a distância (em quilômetros) entre duas coordenadas usando ORS Directions.

        Argumentos:
            coord_origem (list|tuple): Coordenadas de origem como [lon, lat] ou (lon, lat).
            coord_destino (list|tuple): Coordenadas de destino como [lon, lat] ou (lon, lat).

        Retorna:
            float: Distância em quilômetros entre os pontos (valor em km).

        Exemplo de saída:
            12.5  # significa 12.5 km
        """
        url = "https://api.openrouteservice.org/v2/directions/driving-car/json"
        key = ROUTING_API_KEY
        if not key:
            raise RuntimeError("Chave da API de rotas não configurada. Defina a variável de ambiente `ROUTING_API_KEY_FILE` ou `ROUTING_API_KEY`.")

        headers = {"Authorization": key, "Content-Type": "application/json"}
        body = {"coordinates": [coord_origem, coord_destino]}
        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()
        data = response.json()
        print(data)
        distance = data["routes"][0]["summary"]["distance"]/1000
        print(str(distance) + "km")
        #duration = data["routes"][0]["summary"]["duration"]
        return distance
    

    def obter_preco_combustivel(self, estado: str, tipo_combustivel: str = "gasolina") -> Optional[float]:
        """
        Retorna o preço do combustível para um estado brasileiro específico (UF).

        Argumentos:
            estado (str): Código da unidade federativa (ex.: 'sp', 'rj', 'mg')
            tipo_combustivel (str): 'gasolina' ou 'diesel'

        Retorna:
            float ou None: Preço como float (ex.: 6.03) ou None caso não encontrado

        Exemplo de saída:
            6.03  # significa R$ 6,03 por litro
        """

        url = "https://combustivelapi.com.br/api/precos"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        }

        # normaliza o código do estado (UF)
        estado = estado.lower()

        try:
            response = requests.get(url, headers=headers)
            data = response.json()

            prices = data.get("precos", {})
            fuel_data = prices.get(tipo_combustivel)

            if not fuel_data:
                print(f"Tipo de combustível '{tipo_combustivel}' não encontrado.")
                return None

            price = fuel_data.get(estado)

            if price:
                price_float = float(price.replace(",","."))
                return price_float
            else:
                print(f"Estado '{estado}' não encontrado.")
                return None

        except Exception as e:
            print("Erro ao buscar preço do combustível:", e)
            return None





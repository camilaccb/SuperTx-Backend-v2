from pydantic import BaseModel, validator
from datetime import datetime
import re

from model.corrida import Corridas

class CorridaSchema(BaseModel):

    """ 
    Define como uma nova corrida deve ser inserida
    
    """    
    
    id_cliente: str = "83738509020"
    tipo_corrida: str = "aplicativo"
    valor_corrida: float = "10.50"
    origem_corrida:  str = "Rua jaú, 60, Fortaleza, Ceará"
    destino_corrida: str = "Rua Delmiro de Farias,1006, Fortaleza, Ceará"

    @validator('id_cliente')
    def verificar_cpf(cls,v):
        if re.search("[0-9]",v):
            return v
        else:
            raise ValueError("O cpf deve conter apenas números")

    @validator('tipo_corrida')
    def verificar_tipo_corrida(cls,v):
        if v not in ("aplicativo", "cliente", "rua"):
            raise ValueError(f"Tipo de corrida inválido")
        return v
            

class CorridaViewSchema(BaseModel):

    """ 
    Define como uma nova corrida a ser inserida deve ser representada
    
    """    
    id_cliente: str
    tipo_corrida: str
    valor_corrida: float
    hora_registro_corrida: datetime
    distancia_corrida: float
    origem_corrida: str
    destino_corrida: str
    estado_corrida: str
    valor_liquido_corrida: float
    valor_gasolina: float

    
def apresenta_corrida(corrida: Corridas):
    """ 
    Retorna uma representação da corrida
    
    """
    return {
        "id_cliente": corrida.id_cliente,
        "tipo_corrida": corrida.tipo_corrida,
        "valor_corrida": corrida.valor_corrida,
        "hora_registro_corrida": corrida.hora_registro_corrida,
        "origem_corrida": corrida.origem_corrida,
        "destino_corrida": corrida.destino_corrida,
        "distancia_corrida": corrida.distancia_corrida,
        "estado_corrida": corrida.estado_corrida,
        "valor_liquido_corrida": corrida.valor_liquido_corrida,
        "valor_gasolina": corrida.valor_gasolina
    }
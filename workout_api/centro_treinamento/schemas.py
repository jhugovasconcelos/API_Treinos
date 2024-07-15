from typing import Annotated, Optional

from pydantic import UUID4, Field
from workout_api.contrib.schemas import BaseSchema


class CentroTreinamentoIn(BaseSchema):
    nome: Annotated[str, Field(description='Centro de Treinamento', example='CT King', max_length=20)]
    endereco: Annotated[str, Field(description='Endereço do centro de Treinamento', example='Rua das Rosas, 100', max_length=60)]
    proprietario: Annotated[str, Field(description='Proprietário do centro de Treinamento', example='Marcos', max_length=30)]

class CentroTreinamentoAtleta(BaseSchema):
    nome: Annotated[str, Field(description='Nome do Centro de Treinamento', example='CT King', max_length=20)]

class CentroTreinamentoOut(CentroTreinamentoIn):
    id: Annotated[UUID4, Field(description='Identificador do Centro de Treinamento')]

class CentroTreinamentoUpdate(BaseSchema):
    nome: Annotated[Optional[str], Field(None, description='Centro de Treinamento', example='CT King', max_length=20)]
    endereco: Annotated[Optional[str], Field(None, description='Endereço do centro de Treinamento', example='Rua das Rosas, 100', max_length=60)]
    proprietario: Annotated[Optional[str], Field(None, description='Proprietário do centro de Treinamento', example='Marcos', max_length=30)]
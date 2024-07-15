from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, Body, Depends, HTTPException, status
from pydantic import UUID4
from sqlalchemy.future import select
from workout_api.atleta.models import AtletaModel
from workout_api.atleta.schemas import  AtletaIn, AtletaOut, AtletaUpdate, AtletaGetAll
from workout_api.categorias.models import CategoriaModel
from workout_api.centro_treinamento.models import CentroTreinamentoModel
from workout_api.contrib.dependencies import DatabaseDependency
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import Page, Params


router = APIRouter()

####### POST route #######
@router.post(
    '/',
    summary='Criar novo atleta',
    status_code=status.HTTP_201_CREATED,
    response_model=AtletaOut
)
async def post(db_session: DatabaseDependency,atleta_in: AtletaIn = Body(...)) -> AtletaOut:
    
    # Verificação da categoria
    categoria_name = atleta_in.categoria.nome
    categoria =  (await db_session.execute(
        select(CategoriaModel).filter_by(nome=categoria_name))
        ).scalars().first()
    if not categoria:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f'A categoria {categoria_name} não foi encontrada'
        )
    
    # Verificação do CT
    centro_treinamento_name = atleta_in.centro_treinamento.nome
    centro_treinamento =  (await db_session.execute(
        select(CentroTreinamentoModel).filter_by(nome=centro_treinamento_name))
        ).scalars().first()
    if not centro_treinamento:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f'O Centro de treinamento {centro_treinamento_name} não foi encontrado'
        )
    

    # Inserção dos dados do atleta em si
    try:
        atleta_out = AtletaOut(
            id=uuid4(), 
            created_at=datetime.now(),
            **atleta_in.model_dump()
        )
        atleta_model = AtletaModel(**atleta_out.model_dump(exclude={'categoria', 'centro_treinamento'}))
        atleta_model.categoria_id = categoria.pk_id
        atleta_model.centro_treinamento_id = centro_treinamento.pk_id

        db_session.add(atleta_model)
        await db_session.commit()
    except Exception as e: #TODO: Fazer um tratamento mais específico dessa exceção
        if 'duplicate key value' in repr(e):
            raise HTTPException(
                status_code=status.HTTP_303_SEE_OTHER,
                detail=f'Já existe um atleta cadastrado com o CPF: {atleta_in.cpf}'
            )
        else:
            detalhes = {
                "msg": "Ocorreu um erro ao inserir os dados no banco.",
                "cod": f"{e}"
            }
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail= detalhes
            )
    

    return atleta_out

####### GET all route ######
@router.get(
    '/',
    summary='Obter todos os atletas',
    status_code=status.HTTP_200_OK,
    response_model=list[AtletaGetAll]
)
async def query_all(db_session: DatabaseDependency ) -> list[AtletaGetAll]:
    
    atletas: list[AtletaGetAll] = (await db_session.execute(select(AtletaModel))).scalars().all()    
    return [AtletaGetAll.model_validate(atleta) for atleta in atletas]
    


####### GET one route ######
@router.get(
    '/{id}',
    summary='Obter uma atleta pelo ID',
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut
)
async def query_by_id(id:UUID4, db_session: DatabaseDependency) -> AtletaOut:
    atleta: AtletaOut = (
        await db_session.execute(select(AtletaModel).filter_by(id=id))
    ).scalars().first()

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Atleta não encontrado no id: {id}'
        )

    return atleta

@router.get(
    '/buscanome/',
    summary='Obter um atleta pelo nome',
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut
)
async def query_by_nome(db_session: DatabaseDependency, nome: str) -> AtletaOut:
    atleta: AtletaOut = (
        await db_session.execute(select(AtletaModel).filter_by(nome=nome))
    ).scalars().first()
      
    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Atleta {nome} não encontrado'
        )
    return atleta

@router.get(
    '/buscacpf/',
    summary='Obter um atleta pelo cpf',
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut
)
async def query_by_cpf(db_session: DatabaseDependency, cpf: str) -> AtletaOut:
    atleta: AtletaOut = (
        await db_session.execute(select(AtletaModel).filter_by(cpf=cpf))
    ).scalars().first()
      
    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'CPF {cpf} não encontrado'
        )
    return atleta


####### PATCH route #######
@router.patch(
    '/{id}',
    summary='Editar um atleta pelo ID',
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut
)
async def patch(id:UUID4, db_session: DatabaseDependency, atleta_up: AtletaUpdate = Body(...)) -> AtletaOut:
    atleta: AtletaOut = (
        await db_session.execute(select(AtletaModel).filter_by(id=id))
    ).scalars().first()

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Atleta não encontrado no id: {id}'
        )

    atleta_update = atleta_up.model_dump(exclude_unset=True)
    for key,value in atleta_update.items():
        setattr(atleta, key, value)
    await db_session.commit()
    await db_session.refresh(atleta)
    return atleta

####### DELETE route #######
@router.delete(
    '/{id}',
    summary='Excluir um atleta',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete(id:UUID4, db_session: DatabaseDependency) -> None:
    atleta: AtletaOut = (
        await db_session.execute(select(AtletaModel).filter_by(id=id))
    ).scalars().first()

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Atleta não encontrado no id: {id}'
        )
    
    await db_session.delete(atleta)
    await db_session.commit()
    
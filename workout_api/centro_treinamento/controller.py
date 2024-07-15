from uuid import uuid4
from fastapi import APIRouter, Body, status, HTTPException
from pydantic import UUID4
from workout_api.centro_treinamento.models import CentroTreinamentoModel
from workout_api.centro_treinamento.schemas import CentroTreinamentoIn, CentroTreinamentoOut, CentroTreinamentoUpdate
from workout_api.contrib.dependencies import DatabaseDependency
from sqlalchemy.future import select

router = APIRouter()

# POST route
@router.post(
    '/',
    summary='Criar um novo Centro de Treinamento',
    status_code=status.HTTP_201_CREATED,
    response_model=CentroTreinamentoOut
)
async def post(
    db_session: DatabaseDependency,
    centro_treinamento_in: CentroTreinamentoIn = Body(...)
) -> CentroTreinamentoOut:
    centro_treinamento_out = CentroTreinamentoOut(id=uuid4(), **centro_treinamento_in.model_dump())
    centro_treinamento_model = CentroTreinamentoModel(**centro_treinamento_out.model_dump())

    db_session.add(centro_treinamento_model)
    await db_session.commit()

    return centro_treinamento_out

# GET all route
@router.get(
    '/',
    summary='Obter todos os centros_treinamento',
    status_code=status.HTTP_200_OK,
    response_model=list[CentroTreinamentoOut]
)
async def query(db_session: DatabaseDependency) -> list[CentroTreinamentoOut]:
    centros_treinamento: list[CentroTreinamentoOut] = (await db_session.execute(select(CentroTreinamentoModel))).scalars().all()
    return centros_treinamento

# GET one route
@router.get(
    '/{id}',
    summary='Obter um centro de treinamento pelo ID',
    status_code=status.HTTP_200_OK,
    response_model=CentroTreinamentoOut
)
async def query(id:UUID4, db_session: DatabaseDependency) -> CentroTreinamentoOut:
    centro_treinamento: CentroTreinamentoOut = (
        await db_session.execute(select(CentroTreinamentoModel).filter_by(id=id))
    ).scalars().first()

    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Centro de Treinamento não encontrado no id: {id}'
        )

    return centro_treinamento

@router.get(
    '/buscanome/',
    summary='Obter um centro de treinamento pelo nome',
    status_code=status.HTTP_200_OK,
    response_model=CentroTreinamentoOut
)
async def query_by_nome(db_session: DatabaseDependency, nome: str) -> CentroTreinamentoOut:
    centro_treinemanto: CentroTreinamentoOut = (
        await db_session.execute(select(CentroTreinamentoModel).filter_by(nome=nome))
    ).scalars().first()
      
    if not centro_treinemanto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Centro de Treinamento {nome} não encontrado'
        )
    return centro_treinemanto

####### PATCH route #######
@router.patch(
    '/{id}',
    summary='Editar um Centro de Treinamento pelo ID',
    status_code=status.HTTP_200_OK,
    response_model=CentroTreinamentoOut
)
async def patch(id:UUID4, db_session: DatabaseDependency, centro_treinamento_up: CentroTreinamentoUpdate = Body(...)) -> CentroTreinamentoOut:
    centro_treinamento: CentroTreinamentoOut = (
        await db_session.execute(select(CentroTreinamentoModel).filter_by(id=id))
    ).scalars().first()

    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Centro de Treinamento não encontrado no id: {id}'
        )

    centro_treinamento_update = centro_treinamento_up.model_dump(exclude_unset=True)
    for key,value in centro_treinamento_up.items():
        setattr(centro_treinamento, key, value)
    await db_session.commit()
    await db_session.refresh(centro_treinamento)
    return centro_treinamento

####### DELETE route #######
@router.delete(
    '/{id}',
    summary='Excluir um cecntro de treinamento',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete(id:UUID4, db_session: DatabaseDependency) -> None:
    centro_treinamento: CentroTreinamentoOut = (
        await db_session.execute(select(CentroTreinamentoModel).filter_by(id=id))
    ).scalars().first()

    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Centro de Treinamento não encontrado no id: {id}'
        )
    
    await db_session.delete(centro_treinamento)
    await db_session.commit()
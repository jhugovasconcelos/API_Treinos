from uuid import uuid4
from fastapi import APIRouter, Body, status, HTTPException
from pydantic import UUID4
from workout_api.categorias.models import CategoriaModel
from workout_api.categorias.schemas import CategoriaIn, CategoriaOut, CategoriaUpdate
from workout_api.contrib.dependencies import DatabaseDependency
from sqlalchemy.future import select

router = APIRouter()

# POST route
@router.post(
    '/',
    summary='Criar nova categoria',
    status_code=status.HTTP_201_CREATED,
    response_model=CategoriaOut
)
async def post(
    db_session: DatabaseDependency,
    categoria_in: CategoriaIn = Body(...)
) -> CategoriaOut:
    categoria_out = CategoriaOut(id=uuid4(), **categoria_in.model_dump())
    categoria_model = CategoriaModel(**categoria_out.model_dump())

    db_session.add(categoria_model)
    await db_session.commit()

    return categoria_out

# GET all route
@router.get(
    '/',
    summary='Obter todas as categorias',
    status_code=status.HTTP_200_OK,
    response_model=list[CategoriaOut]
)
async def query(db_session: DatabaseDependency) -> list[CategoriaOut]:
    categorias: list[CategoriaOut] = (await db_session.execute(select(CategoriaModel))).scalars().all()
    return categorias

###### GET one route #####
@router.get(
    '/{id}',
    summary='Obter uma categoria pelo ID',
    status_code=status.HTTP_200_OK,
    response_model=CategoriaOut
)
async def query(id:UUID4, db_session: DatabaseDependency) -> CategoriaOut:
    categoria: CategoriaOut = (
        await db_session.execute(select(CategoriaModel).filter_by(id=id))
    ).scalars().first()

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Categoria não encontrada no id: {id}'
        )

    return categoria

@router.get(
    '/buscanome/',
    summary='Obter uma categoria pelo nome',
    status_code=status.HTTP_200_OK,
    response_model=CategoriaOut
)
async def query_by_nome(db_session: DatabaseDependency, nome: str) -> CategoriaOut:
    categoria: CategoriaOut = (
        await db_session.execute(select(CategoriaModel).filter_by(nome=nome))
    ).scalars().first()
      
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Categoria {nome} não encontrada'
        )
    return categoria


####### PATCH route #####
@router.patch(
    '/{id}',
    summary='Editar uma categoria pelo ID',
    status_code=status.HTTP_200_OK,
    response_model=CategoriaOut
)
async def patch(id:UUID4, db_session: DatabaseDependency, categoria_up: CategoriaUpdate = Body(...)) -> CategoriaOut:
    categoria: CategoriaOut = (
        await db_session.execute(select(CategoriaModel).filter_by(id=id))
    ).scalars().first()

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Categoria não encontrada no id: {id}'
        )

    categoria_update = categoria_up.model_dump(exclude_unset=True)
    for key,value in categoria_update.items():
        setattr(categoria, key, value)
    await db_session.commit()
    await db_session.refresh(categoria)
    return categoria

####### DELETE route #######
@router.delete(
    '/{id}',
    summary='Excluir uma categoria',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete(id:UUID4, db_session: DatabaseDependency) -> None:
    categoria: CategoriaOut = (
        await db_session.execute(select(CategoriaModel).filter_by(id=id))
    ).scalars().first()

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Categoria não encontrado no id: {id}'
        )
    
    await db_session.delete(categoria)
    await db_session.commit()
    
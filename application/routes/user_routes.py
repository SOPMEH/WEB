from application.services import Container
from fastapi import APIRouter, Depends, status  # type: ignore
from application.schemas.user_schema import UserRequestSchema

router = APIRouter(
    tags=["users"], responses={404: {"description": "Not found"}}
)

@router.get(
    "/api/v1/users",
    status_code=status.HTTP_200_OK,
    description="Просмотр всех пользователей",
)
async def get_users(container: Container = Depends(),):
    return await container.user_service.get_all()


@router.delete(
    "/api/v1/users/{user_id}/",
    status_code=status.HTTP_200_OK,
    description="Удаление пользователя",
)
async def delete_user(user_id: int, container: Container = Depends(),):
    return await container.user_service.delete_user(user_id=user_id)


@router.post(
    "/api/v1/users",
    status_code=status.HTTP_200_OK,
    description="Создание пользователя",
)
async def create_user(data: UserRequestSchema, container: Container = Depends(),):
    return await container.user_service.create_user(data=data.model_dump())


@router.put(
    "/api/v1/users",
    status_code=status.HTTP_200_OK,
    description="Обновление пользователя по id",
)
async def update_user(data: UserRequestSchema, container: Container = Depends(),):
    return await container.user_service.update_user(data=data.model_dump())


from pydantic import BaseModel, Field  # type: ignore

class UserRequestSchema(BaseModel):
    id: int = Field(title="Идентификатор пользователя",)
    username: str = Field(
        title="Имя пользователя", min_length=3, max_length=20,
    )
    password: str = Field(
        title="Пароль пользователя", min_length=3, max_length=20,
    )
    email: str = Field(
        title="Email пользователя", min_length=7, max_length=30,
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "test",
                "password": "test",
                "email": "test@gmail.com",
            }
        }
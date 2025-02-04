from typing import List, Dict 
from application.services.base import Service
from passlib.context import CryptContext  # type: ignore
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession # type: ignore
from sqlalchemy.orm import declarative_base, sessionmaker # type: ignore
from sqlalchemy import Column, Integer, String # type: ignore
from sqlalchemy.future import select # type: ignore
from sqlalchemy.exc import SQLAlchemyError # type: ignore
import greenlet # type: ignore

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DATABASE_URL = "sqlite+aiosqlite:///./example.db"
engine = create_async_engine(DATABASE_URL, echo=True)
Base = declarative_base()
async_session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)


class UserService(Service):

    def __init__(self, request=None): 
        super().__init__(request) 
        self.async_session = async_session
        
    def _hash_password(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    async def get_all(self) -> List[Dict[str, int | str]]: # Получение всех пользователей
        async with self.async_session() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
            return [
                {
                    "id": user.id,
                    "username": user.username,
                    "password": "***hidden***",  # Не возвращаем хэш пароля
                    "email": user.email
                }
                for user in users
            ] # в виде словаря
    
    async def delete_user(self, user_id: int) -> Dict[str, int]: # Удаление пользователя
        async with self.async_session() as session:
            try:
                result = await session.execute(select(User).filter_by(id=user_id))
                user = result.scalar_one_or_none()
                if user:
                    await session.delete(user)
                    await session.commit()
                    return {"success": 200}
                return {"error": 404}
            except SQLAlchemyError:
                return {"error": 500}
     
    async def create_user(self, data: Dict[str, int | str]) -> Dict[str, int | str]:
        async with self.async_session() as session:
            async with session.begin():
                hashed_password = self._hash_password(data["password"])
                new_user = User(username=data["username"], password=hashed_password, email=data["email"])
                session.add(new_user)
                await session.commit()
                data["id"] = new_user.id
                data["password"] = "***hidden***"
                return data
    
    async def update_user(self, data: Dict[str, int | str]) -> Dict[str, int | str]: # Обновление пользователя
        async with self.async_session() as session:
            try:
                result = await session.execute(select(User).filter_by(id=data["id"]))
                user = result.scalar_one_or_none()
                if user:
                    user.username = data["username"]
                    user.password = self._hash_password(data["password"])
                    user.email = data["email"]
                    await session.commit()
                    data["password"] = "***hidden***"  # Не возвращаем хэш пароля
                    return data
                return {"error": 404}
            except SQLAlchemyError:
                return {"error": 500}

    def __del__(self):
        pass

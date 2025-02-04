from typing import List, Dict 
from application.services.base import Service
import sqlite3
from passlib.context import CryptContext  # type: ignore
from sqlalchemy.ext.asyncio import create_async_engine # type: ignore
from sqlalchemy.orm import declarative_base # type: ignore
from sqlalchemy import Column, Integer, String # type: ignore

# А тут я удалил временную базу данных

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DATABASE_URL = "sqlite+aiosqlite:///./example.db"
engine = create_async_engine(DATABASE_URL, echo=True)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)


class UserService(Service):

    def __init__(self, request=None): 
        super().__init__(request) 
        self.conn = None 
        try:
            self.conn = sqlite3.connect('example.db')
            self.cursor = self.conn.cursor()
        except sqlite3.Error:
            if self.conn:
                self.conn.close()
            raise
        
    def _hash_password(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    async def get_all(self) -> List[Dict[str, int | str]]: # Получение всех пользователей
        self.cursor.execute('SELECT * FROM users')
        rows = self.cursor.fetchall()
        return [
            {
                "id": row[0],
                "username": row[1],
                "password": "***hidden***",  # Не возвращаем хэш пароля
                "email": row[3]
            }
            for row in rows
        ] # в виде словаря
    
    async def delete_user(self, user_id: int) -> Dict[str, int]: # Удаление пользователя
        try:
            self.cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            if self.cursor.rowcount > 0:
                self.conn.commit()
                return {"success": 200}
            return {"error": 404}
        except sqlite3.Error:
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
        try:
            hashed_password = self._hash_password(data["password"])
            self.cursor.execute(
                'UPDATE users SET username = ?, password = ?, email = ? WHERE id = ?',
                (data["username"], hashed_password, data["email"], data["id"])
            )
            if self.cursor.rowcount > 0:
                self.conn.commit()
                data["password"] = "***hidden***"  # Не возвращаем хэш пароля
                return data
            return {"error": 404}
        except sqlite3.Error:
            return {"error": 500}

    def __del__(self):
        if hasattr(self, 'conn') and self.conn:  # Проверяем существование атрибута
            self.conn.close()

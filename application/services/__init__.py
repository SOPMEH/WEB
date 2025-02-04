from functools import cached_property
from fastapi.requests import Request
from application.services.user_service import UserService



class Container:
    def __init__(self, request: Request) -> None:
        self.request = request

    @cached_property # чтобы этот экземпляр не создавался заново при каждом обращении
    def user_service(self) -> UserService:
        return UserService(self.request)
    
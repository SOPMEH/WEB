from typing import Optional
from starlette.requests import Request


class Service:
    def __init__(self, request: Optional[Request]) -> None:
        self.request = request

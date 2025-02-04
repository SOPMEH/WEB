from fastapi import FastAPI  # type: ignore
from application.routes.user_routes import router as users_router

app = FastAPI()
app.include_router(users_router)

if __name__ == "__main__":
    # python3 -m application.main
    import uvicorn  # type: ignore
    uvicorn.run(app, host="127.0.0.1", port=8000)



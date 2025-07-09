from fastapi import FastAPI
from starlette.responses import RedirectResponse

from src.users.router import router as user_router
from src.auth.router import router as auth_router

app = FastAPI(name="JWTAuthFastAPI", version="0.0.1")

app.include_router(user_router)
app.include_router(auth_router)


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

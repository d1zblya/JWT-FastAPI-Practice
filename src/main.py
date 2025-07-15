from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from src.auth.router import router as auth_router
from src.business.router import router as business_router
from src.core.config import settings
from src.core.exception_handlers import add_exception_handlers
from src.users.router import router as user_router

app: FastAPI = FastAPI(name="JWTAuthFastAPI", version="0.0.1")

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(business_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Set-Cookie", "Authorization", "Access-Control-Allow-Origin",
                   "Access-Control-Allow-Headers", "Content-Type"]
)

add_exception_handlers(app)


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

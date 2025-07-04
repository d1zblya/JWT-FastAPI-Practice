from fastapi import FastAPI
from starlette.responses import RedirectResponse

app = FastAPI(name="JWTAuthFastAPI", version="0.0.1")


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

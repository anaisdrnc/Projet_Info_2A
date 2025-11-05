import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from .MovieController import movie_router
from .UserController import user_router
from .Product_API import product_router

app = FastAPI(title="Projet Info 2A", description="UB'EJR")
app.include_router(user_router)
app.include_router(movie_router)
app.include_router(product_router)


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")


def run_app():
    uvicorn.run("src.App.API:app", host="0.0.0.0", port=8000, reload=True)

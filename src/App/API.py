import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from src.App.AdministratorController import admin_router
from src.App.DriverController import driver_router
from src.App.OrderController import order_router
from src.App.ProductController import product_router

app = FastAPI(title="Projet Info 2A", description="UB'EJR")
app.include_router(product_router)
app.include_router(order_router)
app.include_router(admin_router)
app.include_router(driver_router)


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """
    Redirects the root URL to the interactive API documentation (/docs).
    Useful to directly open Swagger UI when accessing the server.
    """
    return RedirectResponse(url="/docs")


def run_app():
    """
    Starts the FastAPI application using Uvicorn.
    - Runs on host 0.0.0.0 (accessible from outside container)
    - Port 8000
    - Reload enabled for development
    """
    uvicorn.run("src.App.API:app", host="0.0.0.0", port=8000, reload=True)

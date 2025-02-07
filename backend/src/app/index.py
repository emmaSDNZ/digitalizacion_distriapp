import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from fastapi import FastAPI

from routes.route_masterproductos import router as route_master_productos
from routes.route_proveedor import router as route_proveedor

app = FastAPI()

# Agregar la raíz del proyecto al path de Python
sys.path.append(os.path.abspath(".."))

@app.get('/', tags=["root"], status_code=200)
async def root():
    # results = await {"message" : "Bievenidos a la API Dsitrimed"}
    return {"message" : "Bievenidos a la API Dsitrimed"}

app.include_router(route_master_productos)
app.include_router(route_proveedor)


from fastapi import FastAPI

app = FastAPI()

@app.get("/services")
def read_root():
    return {"MicroServices": "Servicios de Productos"}


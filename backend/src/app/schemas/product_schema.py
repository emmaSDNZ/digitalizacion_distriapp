#Usamos Pydantic para definir cómo deben verse los datos.
from pydantic import BaseModel

class HealthCheckSchema(BaseModel):
    status: str
    result: list
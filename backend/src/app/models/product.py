from pydantic import BaseModel

class HealthCheckModel(BaseModel):
    status: str
    result: list

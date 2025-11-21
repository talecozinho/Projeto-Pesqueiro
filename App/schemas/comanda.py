from pydantic import BaseModel
from datetime import datetime

class ComandaBase(BaseModel):
    cliente_id: int

class ComandaCreate(ComandaBase):
    pass

class ComandaResponse(ComandaBase):
    id: int
    status: str
    valor_total: float
    criado_em: datetime

    class Config:
        from_attributes = True
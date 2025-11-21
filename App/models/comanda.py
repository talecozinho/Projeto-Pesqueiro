from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from App.db.connection import Base

class Comanda(Base):
    __tablename__ = "comandas"

    id = Column(Integer, primary_key=True, index=True)
    # AQUI ESTÁ O SEGREDO: Linkamos com o id da tabela clientes
    cliente_id = Column(Integer, ForeignKey("clientes.id")) 
    
    status = Column(String, default="ABERTA") # Status: ABERTA, FECHADA, PAGA
    valor_total = Column(Float, default=0.0)  # Começa zerada
    criado_em = Column(DateTime(timezone=True), server_default=func.now()) # Data automática

    # Isso permite que, acessando a comanda, a gente saiba os dados do cliente automaticamente
    cliente = relationship("Cliente")
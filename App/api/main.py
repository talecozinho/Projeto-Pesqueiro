from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from App.db.connection import engine, Base, get_db
# Models
from App.models.cliente import Cliente
from App.models.comanda import Comanda
from App.models.item import ItemComanda
# Schemas
from App.schemas.cliente import ClienteCreate, ClienteResponse
from App.schemas.comanda import ComandaCreate, ComandaResponse
from App.schemas.item import ItemCreate, ItemResponse

# Cria todas as tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Pesqueiro Manager API",
    description="Sistema de Gestão de Clientes e Consumo",
    version="1.0.0"
)

# Configuração CORS (Para o site funcionar)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "Online", "modulo": "Gestão de Comandas"}

# --- CLIENTES ---
@app.post("/clientes", response_model=ClienteResponse)
def criar_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    db_cliente = Cliente(**cliente.model_dump())
    db.add(db_cliente)
    try:
        db.commit()
        db.refresh(db_cliente)
        return db_cliente
    except Exception:
        raise HTTPException(status_code=400, detail="Erro. CPF já cadastrado?")

@app.get("/clientes", response_model=List[ClienteResponse])
def listar_clientes(db: Session = Depends(get_db)):
    return db.query(Cliente).all()

# --- COMANDAS ---
@app.post("/comandas", response_model=ComandaResponse)
def abrir_comanda(comanda: ComandaCreate, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == comanda.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    db_comanda = Comanda(cliente_id=comanda.cliente_id)
    db.add(db_comanda)
    db.commit()
    db.refresh(db_comanda)
    return db_comanda

@app.get("/comandas/{comanda_id}", response_model=ComandaResponse)
def ver_comanda(comanda_id: int, db: Session = Depends(get_db)):
    # Adicionamos o .options(joinedload(Comanda.itens)) para carregar a lista de itens
    # O Pydantic (Schema) faz o resto do trabalho de formatação
    comanda = db.query(Comanda).filter(Comanda.id == comanda_id).first()
    if not comanda:
        raise HTTPException(status_code=404, detail="Comanda não encontrada")
    return comanda

# --- ITENS (CONSUMO) ---
@app.post("/itens", response_model=ItemResponse)
def adicionar_item(item: ItemCreate, db: Session = Depends(get_db)):
    comanda = db.query(Comanda).filter(Comanda.id == item.comanda_id).first()
    
    if not comanda:
        raise HTTPException(status_code=404, detail="Comanda não encontrada")
    if comanda.status != "ABERTA":
        raise HTTPException(status_code=400, detail="Comanda já está fechada!")

    db_item = ItemComanda(**item.model_dump())
    db.add(db_item)
    comanda.valor_total += (item.quantidade * item.preco_unitario)
    
    db.commit()
    db.refresh(db_item)
    return db_item

# --- NOVO: CHECKOUT / FECHAMENTO DE CONTA ---
@app.put("/comandas/{comanda_id}/checkout", response_model=ComandaResponse)
def finalizar_comanda(comanda_id: int, db: Session = Depends(get_db)):
    """
    Finaliza a comanda, mudando seu status para 'PAGA'. 
    A conta fica travada contra novos pedidos.
    """
    comanda = db.query(Comanda).filter(Comanda.id == comanda_id).first()
    
    if not comanda:
        raise HTTPException(status_code=404, detail="Comanda não encontrada")
    
    if comanda.status != "ABERTA":
        raise HTTPException(status_code=400, detail=f"Comanda já está {comanda.status}.")

    comanda.status = "PAGA"
    db.commit()
    db.refresh(comanda)
    
    return comanda
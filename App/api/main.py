from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from App.db.connection import engine, Base, get_db
# Imports dos Modelos (Banco)
from App.models.cliente import Cliente
from App.models.comanda import Comanda
from App.models.item import ItemComanda # <--- NOVO IMPORT

# Imports dos Schemas (Validação)
from App.schemas.cliente import ClienteCreate, ClienteResponse
from App.schemas.comanda import ComandaCreate, ComandaResponse
from App.schemas.item import ItemCreate, ItemResponse # <--- NOVO IMPORT

# Cria todas as tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Pesqueiro Manager API",
    description="Sistema de Gestão Integrada para Pesqueiros",
    version="0.1.0"
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
    return {"status": "Sistema Operacional"}

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
        raise HTTPException(status_code=400, detail="Erro ao cadastrar. CPF duplicado?")

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

# --- NOVO: ADICIONAR ITENS (O Pulo do Gato) ---
@app.post("/itens", response_model=ItemResponse)
def adicionar_item(item: ItemCreate, db: Session = Depends(get_db)):
    """
    Adiciona um produto na comanda e atualiza o valor total automaticamente.
    """
    # 1. Acha a comanda no banco
    comanda = db.query(Comanda).filter(Comanda.id == item.comanda_id).first()
    
    if not comanda:
        raise HTTPException(status_code=404, detail="Comanda não encontrada")
    
    if comanda.status != "ABERTA":
        raise HTTPException(status_code=400, detail="Esta comanda já está fechada!")

    # 2. Cria o item
    db_item = ItemComanda(**item.model_dump())
    db.add(db_item)
    
    # 3. Lógica de Negócio: Calcula o subtotal e soma na Comanda
    subtotal = item.quantidade * item.preco_unitario
    comanda.valor_total += subtotal  # <--- AQUI ACONTECE A SOMA AUTOMÁTICA

    # 4. Salva tudo de uma vez
    db.commit()
    db.refresh(db_item)
    return db_item

# --- NOVO: CONSULTAR UMA COMANDA ESPECÍFICA ---
@app.get("/comandas/{comanda_id}", response_model=ComandaResponse)
def ver_comanda(comanda_id: int, db: Session = Depends(get_db)):
    """
    Mostra o status atual da comanda e o valor total a pagar.
    """
    comanda = db.query(Comanda).filter(Comanda.id == comanda_id).first()
    
    if not comanda:
        raise HTTPException(status_code=404, detail="Comanda não encontrada")
        
    return comanda
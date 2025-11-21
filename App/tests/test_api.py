from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from App.api.main import app, get_db
from App.db.connection import Base

# 1. Configura um Banco de Dados de Teste (Na memória, para não sujar o real)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cria as tabelas no banco de teste
Base.metadata.create_all(bind=engine)

# Substitui o banco real pelo banco de teste
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# --- OS TESTES COMEÇAM AQUI ---

def test_fluxo_completo_pesqueiro():
    """
    Teste de Integração:
    1. Cria Cliente
    2. Abre Comanda
    3. Lança Item
    4. Verifica se o total foi calculado certo
    """
    
    # 1. Cadastrar Cliente
    response = client.post("/clientes", json={"nome": "Tester", "cpf": "99988877700", "telefone": "", "email": ""})
    assert response.status_code == 200
    data_cliente = response.json()
    cliente_id = data_cliente["id"]
    
    # 2. Abrir Comanda
    response = client.post("/comandas", json={"cliente_id": cliente_id})
    assert response.status_code == 200
    data_comanda = response.json()
    comanda_id = data_comanda["id"]
    assert data_comanda["valor_total"] == 0  # Tem que começar zerada
    
    # 3. Lançar Item (2 Cervejas a R$ 10,00)
    item_payload = {
        "comanda_id": comanda_id,
        "nome_produto": "Cerveja Teste",
        "quantidade": 2,
        "preco_unitario": 10.0
    }
    response = client.post("/itens", json=item_payload)
    assert response.status_code == 200
    
    # 4. A PROVA FINAL: Consultar se o valor subiu para 20.0
    response = client.get(f"/comandas/{comanda_id}")
    assert response.status_code == 200
    dados_finais = response.json()
    
    # O teste falha se o valor não for 20.0
    assert dados_finais["valor_total"] == 20.0
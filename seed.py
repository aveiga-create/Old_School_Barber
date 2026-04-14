from app import app, db
from models import Barbeiro

with app.app_context():
    # 1. CRIA TODAS AS TABELAS PRIMEIRO
    db.create_all()
    
    # 2. DEPOIS INSERE OS DADOS
    barbeiros = [
        Barbeiro(nome="Carlos Silva", especialidade="Cortes clássicos", foto="carlos.jpg"),
        Barbeiro(nome="João Mendes", especialidade="Fade e degradê", foto="joao.jpg")
    ]

    db.session.add_all(barbeiros)
    db.session.commit()

    print("Banco de dados criado e barbeiros adicionados com sucesso!")
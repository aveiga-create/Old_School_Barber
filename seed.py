from app import app, db
from models import Barbeiro, Servico # <-- Adicionamos o import do Servico aqui

with app.app_context():
    # 1. Cria as tabelas
    db.create_all()
    
    # 2. Adiciona os Barbeiros (Verifique se o '.jpg' ou '.png' está EXATAMENTE igual ao arquivo)
    barbeiros = [
        Barbeiro(nome="Carlos Silva", especialidade="Cortes clássicos", foto="carlos.jpg"),
        Barbeiro(nome="João Mendes", especialidade="Fade e degradê", foto="joao.jpg")
    ]
    db.session.add_all(barbeiros)

    # 3. Adiciona os Serviços
    servicos = [
        Servico(nome="Corte Clássico", preco=35.00),
        Servico(nome="Barba Tradicional", preco=25.00),
        Servico(nome="Corte + Barba", preco=55.00),
        Servico(nome="Tratamento Premium", preco=70.00)
    ]
    db.session.add_all(servicos)

    db.session.commit()

    print("Banco de dados criado com barbeiros e serviços!")
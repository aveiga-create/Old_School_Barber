from app import app, db
from models import Barbeiro, Servico

with app.app_context():
    # 1. Cria as tabelas
    db.create_all()
    
    # 2. Adiciona os Barbeiros (Agora com a extensão correta .png)
    barbeiros = [
        Barbeiro(nome="Carlos Silva", especialidade="Cortes clássicos", foto="carlos.png"),
        Barbeiro(nome="João Mendes", especialidade="Fade e degradê", foto="joao.png")
    ]
    db.session.add_all(barbeiros)

    # 3. Adiciona os Serviços para o agendamento funcionar (Todos com 30 min)
    servicos = [
        Servico(nome="Corte Clássico", duracao_minutos=30, preco=35.00),
        Servico(nome="Barba Tradicional", duracao_minutos=30, preco=25.00),
        Servico(nome="Corte + Barba", duracao_minutos=30, preco=55.00),
        Servico(nome="Tratamento Premium", duracao_minutos=30, preco=70.00)
    ]
    db.session.add_all(servicos)

    db.session.commit()

    print("Banco de dados atualizado com fotos em PNG e serviços de 30 minutos adicionados!")
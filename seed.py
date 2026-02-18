from app import app, db
from models import Barbeiro

with app.app_context():
    barbeiros = [
        Barbeiro(nome="Carlos Silva", especialidade="Cortes clássicos", foto="carlos.jpg"),
        Barbeiro(nome="João Mendes", especialidade="Fade e degradê", foto="joao.jpg")
    ]

    db.session.add_all(barbeiros)
    db.session.commit()

    print("Barbeiros adicionados com sucesso!")

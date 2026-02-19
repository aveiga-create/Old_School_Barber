from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import Numeric

db = SQLAlchemy()


# ==========================================
# USUÁRIO
# ==========================================
class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    agendamentos = db.relationship(
        "Agendamento",
        backref="cliente",
        lazy="select",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Usuario {self.email}>"


# ==========================================
# BARBEIRO
# ==========================================
class Barbeiro(db.Model):
    __tablename__ = "barbeiros"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especialidade = db.Column(db.String(150))
    foto = db.Column(db.String(200))
    ativo = db.Column(db.Boolean, default=True)

   agendamentos = db.relationship(
    "Agendamento",
    back_populates="barbeiro",
    lazy="select",
    cascade="all, delete-orphan"
)


    def __repr__(self):
        return f"<Barbeiro {self.nome}>"


# ==========================================
# SERVIÇO
# ==========================================
class Servico(db.Model):
    __tablename__ = "servicos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    duracao_minutos = db.Column(db.Integer, nullable=False)
    preco = db.Column(Numeric(10, 2), nullable=False)  # melhor que Float

    def __repr__(self):
        return f"<Servico {self.nome}>"


# ==========================================
# AGENDAMENTO
# ==========================================
class Agendamento(db.Model):
    __tablename__ = "agendamentos"

    id = db.Column(db.Integer, primary_key=True)

    cliente_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    barbeiro_id = db.Column(db.Integer, db.ForeignKey("barbeiros.id"), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey("servicos.id"), nullable=False)

    data = db.Column(db.Date, nullable=False)
    horario = db.Column(db.Time, nullable=False)

    # STATUS DO AGENDAMENTO
    status = db.Column(db.String(50), default="Confirmado")

    # PAGAMENTO
    forma_pagamento = db.Column(db.String(20), nullable=False)
    status_pagamento = db.Column(db.String(20), default="Pendente")

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    servico = db.relationship("Servico", lazy="joined")
    barbeiro = db.relationship("Barbeiro", back_populates="agendamentos")


    # Impede dois agendamentos no mesmo horário para o mesmo barbeiro
    __table_args__ = (
        db.UniqueConstraint("barbeiro_id", "data", "horario", name="unique_agendamento"),
    )

    def __repr__(self):
        return f"<Agendamento {self.data} {self.horario}>"

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, date

from models import db, Usuario, Agendamento, Barbeiro, Servico

app = Flask(__name__)
app.config.from_object("config")

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# ==========================================
# LOGIN MANAGER
# ==========================================
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


# ==========================================
# FUNÇÃO DE HORÁRIOS (AJUSTADA)
# ==========================================
def gerar_horarios(data, barbeiro_id):
    horarios_padrao = [
        "08:00", "09:00", "10:00",
        "11:00", "13:00", "14:00",
        "15:00", "16:00", "17:00"
    ]

    agendamentos = Agendamento.query.filter(
        Agendamento.data == data,
        Agendamento.barbeiro_id == barbeiro_id,
        Agendamento.status != "Cancelado"
    ).all()

    horarios_ocupados = [
        ag.horario.strftime("%H:%M") for ag in agendamentos
    ]

    lista = []

    for h in horarios_padrao:
        if h in horarios_ocupados:
            lista.append((h, "ocupado"))
        else:
            lista.append((h, "livre"))

    return lista


# ==========================================
# HOME
# ==========================================
@app.route("/")
def index():
    barbeiros = Barbeiro.query.filter_by(ativo=True).all()
    return render_template("index.html", barbeiros=barbeiros)


# ==========================================
# AGENDAMENTO (COM CALENDÁRIO)
# ==========================================
@app.route("/agendamento/<int:barbeiro_id>", methods=["GET", "POST"])
@login_required
def agendamento(barbeiro_id):
    # 📅 NOVO: recebe data do formulário
    if request.method == "POST":
        data_str = request.form.get("data")
        data = datetime.strptime(data_str, "%Y-%m-%d").date()
    else:
        data = date.today()

    horarios = gerar_horarios(data, barbeiro_id)

    barbeiro = Barbeiro.query.get_or_404(barbeiro_id)

    return render_template(
        "agendamento.html",
        horarios=horarios,
        barbeiro=barbeiro,
        barbeiro_id=barbeiro_id,
        data=data  # 📅 NOVO
    )


# ==========================================
# CRIAR AGENDAMENTO (AJUSTADO PARA DATA)
# ==========================================
@app.route("/agendar/<int:barbeiro_id>/<horario>")
@login_required
def agendar(barbeiro_id, horario):
    # 📅 NOVO: pega data da URL
    data_str = request.args.get("data")

    if not data_str:
        flash("Data inválida!", "danger")
        return redirect(url_for("agendamento", barbeiro_id=barbeiro_id))

    data = datetime.strptime(data_str, "%Y-%m-%d").date()
    hora = datetime.strptime(horario, "%H:%M").time()

    # 🔒 validação correta
    existente = Agendamento.query.filter(
        Agendamento.barbeiro_id == barbeiro_id,
        Agendamento.data == data,
        Agendamento.horario == hora,
        Agendamento.status != "Cancelado"
    ).first()

    if existente:
        flash("Horário já ocupado!", "danger")
        return redirect(url_for("agendamento", barbeiro_id=barbeiro_id))

    servico = Servico.query.first()

    novo = Agendamento(
        cliente_id=current_user.id,
        barbeiro_id=barbeiro_id,
        servico_id=servico.id,
        data=data,
        horario=hora,
        forma_pagamento="Não definido",
        status="Confirmado"
    )

    db.session.add(novo)
    db.session.commit()

    flash("Agendamento realizado com sucesso!", "success")
    return redirect(url_for("meus_agendamentos"))


# ==========================================
# MEUS AGENDAMENTOS (SEM ALTERAÇÃO)
# ==========================================
@app.route("/meus-agendamentos")
@login_required
def meus_agendamentos():
    agendamentos = Agendamento.query.filter_by(
        cliente_id=current_user.id
    ).order_by(Agendamento.data).all()

    return render_template(
        "meus_agendamentos.html",
        agendamentos=agendamentos
    )


# ==========================================
# CANCELAR AGENDAMENTO (SEM ALTERAÇÃO)
# ==========================================
@app.route("/cancelar/<int:id>")
@login_required
def cancelar_agendamento(id):
    agendamento = Agendamento.query.get_or_404(id)

    if agendamento.cliente_id != current_user.id:
        flash("Ação não permitida!", "danger")
        return redirect(url_for("meus_agendamentos"))

    agendamento.status = "Cancelado"
    db.session.commit()

    flash("Agendamento cancelado!", "info")
    return redirect(url_for("meus_agendamentos"))


# ==========================================
# LOGIN
# ==========================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        user = Usuario.query.filter_by(email=email).first()

        if user and user.senha == senha:
            login_user(user)
            return redirect(url_for("index"))

        flash("Login inválido", "danger")

    return render_template("login.html")


# ==========================================
# LOGOUT
# ==========================================
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# ==========================================
# RODAR APP
# ==========================================
if __name__ == "__main__":
    app.run(debug=True)


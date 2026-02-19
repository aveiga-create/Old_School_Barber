from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models import db, Usuario, Barbeiro, Servico, Agendamento
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Você precisa estar logado para acessar essa página."


# ==========================================
# LOGIN MANAGER
# ==========================================

@login_manager.user_loader
def load_user(user_id):
    # Forma atualizada (evita deprecated)
    return db.session.get(Usuario, int(user_id))


# ==========================================
# ROTAS
# ==========================================

@app.route("/")
def index():
    barbeiros = Barbeiro.query.filter_by(ativo=True).all()
    return render_template("index.html", barbeiros=barbeiros)


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        if not email or not senha:
            flash("Preencha todos os campos.")
            return redirect(url_for("login"))

        user = Usuario.query.filter_by(email=email).first()

        if user and check_password_hash(user.senha, senha):
            login_user(user)
            flash("Login realizado com sucesso!")
            return redirect(url_for("agendamento"))
        else:
            flash("Email ou senha inválidos.")

    return render_template("login.html")


# ---------------- CADASTRO ----------------
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")

        if not nome or not email or not senha:
            flash("Preencha todos os campos.")
            return redirect(url_for("cadastro"))

        if Usuario.query.filter_by(email=email).first():
            flash("Email já cadastrado.")
            return redirect(url_for("cadastro"))

        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha=generate_password_hash(senha),
        )

        db.session.add(novo_usuario)
        db.session.commit()

        flash("Cadastro realizado com sucesso!")
        return redirect(url_for("login"))

    return render_template("cadastro.html")


# ---------------- ESQUECI SENHA ----------------
@app.route("/esqueci-senha", methods=["GET", "POST"])
def esqueci_senha():
    if request.method == "POST":
        flash("Função de recuperação ainda não implementada.")
        return redirect(url_for("login"))

    return render_template("esqueci_senha.html")


# ---------------- AGENDAMENTO ----------------
@app.route("/agendamento", methods=["GET", "POST"])
@login_required
def agendamento():

    barbeiros = Barbeiro.query.filter_by(ativo=True).all()
    servicos = Servico.query.all()

    if request.method == "POST":
        barbeiro_id = request.form.get("barbeiro")
        servico_id = request.form.get("servico")
        data = request.form.get("data")
        horario = request.form.get("horario")
        forma_pagamento = request.form.get("forma_pagamento")

        # Validação
        if not all([barbeiro_id, servico_id, data, horario, forma_pagamento]):
            flash("Preencha todos os campos.")
            return redirect(url_for("agendamento"))

        try:
            # Define status automático
            if forma_pagamento == "Pix":
                status_pagamento = "Pago"
            else:
                status_pagamento = "Pendente"

            novo_agendamento = Agendamento(
                cliente_id=current_user.id,
                barbeiro_id=int(barbeiro_id),
                servico_id=int(servico_id),
                data=datetime.strptime(data, "%Y-%m-%d").date(),
                horario=datetime.strptime(horario, "%H:%M").time(),
                forma_pagamento=forma_pagamento,
                status_pagamento=status_pagamento
            )

            db.session.add(novo_agendamento)
            db.session.commit()

            flash("Agendamento realizado com sucesso!")
            return redirect(url_for("agendamento"))

        except Exception:
            db.session.rollback()
            flash("Esse horário já está ocupado!")

    # 🔹 Lista os agendamentos do usuário
    agendamentos = (
        Agendamento.query
        .filter_by(cliente_id=current_user.id)
        .order_by(Agendamento.data.desc())
        .all()
    )

    return render_template(
        "agendamento.html",
        barbeiros=barbeiros,
        servicos=servicos,
        agendamentos=agendamentos
    )


# ---------------- MEUS AGENDAMENTOS ----------------
@app.route("/meus-agendamentos")
@login_required
def meus_agendamentos():

    agendamentos = (
        Agendamento.query
        .filter_by(cliente_id=current_user.id)
        .order_by(Agendamento.data.desc())
        .all()
    )

    return render_template(
        "meus_agendamentos.html",
        agendamentos=agendamentos
    )


# ---------------- LOGOUT ----------------
from flask import flash

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da sua conta com sucesso!')
    return redirect(url_for('index'))



# ==========================================
# CRIAR BANCO
# ==========================================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

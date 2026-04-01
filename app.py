from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models import db, Usuario, Barbeiro, Servico, Agendamento
from datetime import datetime, date, timedelta
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Você precisa estar logado para acessar essa página."


# ==========================================
# FERIADOS
# ==========================================
FERIADOS = [
    "2026-01-01",
    "2026-12-25",
]


# ==========================================
# LOGIN MANAGER
# ==========================================
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, int(user_id))


# ==========================================
# ROTAS
# ==========================================

@app.route("/")
def index():
    barbeiros = Barbeiro.query.filter_by(ativo=True).all()
    return render_template("index.html", barbeiros=barbeiros)


# ---------------- HORÁRIOS OCUPADOS ----------------
@app.route("/horarios-ocupados")
@login_required
def horarios_ocupados():
    barbeiro_id = request.args.get("barbeiro_id")
    data = request.args.get("data")

    if not barbeiro_id or not data:
        return jsonify([])

    try:
        data_obj = datetime.strptime(data, "%Y-%m-%d").date()
    except ValueError:
        return jsonify([])

    agendamentos = Agendamento.query.filter_by(
        barbeiro_id=int(barbeiro_id),
        data=data_obj
    ).all()

    horarios = [
        ag.horario.strftime("%H:%M") for ag in agendamentos
    ]

    return jsonify(horarios)


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").lower().strip()
        senha = request.form.get("senha")

        if not email or not senha:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"success": False, "message": "Preencha todos os campos"})
            flash("Preencha todos os campos.")
            return redirect(url_for("login"))

        user = Usuario.query.filter_by(email=email).first()

        if user and check_password_hash(user.senha, senha):
            login_user(user)

            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"success": True})

            flash("Login realizado com sucesso!")
            return redirect(url_for("agendamento"))

        else:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"success": False, "message": "Email ou senha inválidos"})

            flash("Email ou senha inválidos.")

    return render_template("login.html")


# ---------------- CADASTRO ----------------
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email", "").lower().strip()
        senha = request.form.get("senha")

        if not nome or not email or not senha:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"success": False, "message": "Preencha todos os campos"})
            flash("Preencha todos os campos.")
            return redirect(url_for("cadastro"))

        if Usuario.query.filter_by(email=email).first():
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"success": False, "message": "Email já cadastrado"})
            flash("Email já cadastrado.")
            return redirect(url_for("cadastro"))

        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha=generate_password_hash(senha),
        )

        db.session.add(novo_usuario)
        db.session.commit()

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": True})

        flash("Cadastro realizado com sucesso!")
        return redirect(url_for("login"))

    return render_template("cadastro.html")


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

        if not all([barbeiro_id, servico_id, data, horario, forma_pagamento]):
            flash("Preencha todos os campos.")
            return redirect(url_for("agendamento"))

        try:
            data_obj = datetime.strptime(data, "%Y-%m-%d").date()
            horario_obj = datetime.strptime(horario, "%H:%M").time()
        except ValueError:
            flash("Data ou horário inválido.")
            return redirect(url_for("agendamento"))

        # 🔒 BLOQUEIOS
        if data_obj < date.today():
            flash("Não é possível agendar em datas passadas.")
            return redirect(url_for("agendamento"))

        if data_obj.weekday() == 6:
            flash("Não atendemos aos domingos.")
            return redirect(url_for("agendamento"))

        if data in FERIADOS:
            flash("Não atendemos em feriados.")
            return redirect(url_for("agendamento"))

        existe = Agendamento.query.filter_by(
            barbeiro_id=int(barbeiro_id),
            data=data_obj,
            horario=horario_obj
        ).first()

        if existe:
            flash("Esse horário já está ocupado!")
            return redirect(url_for("agendamento"))

        status_pagamento = "Pago" if forma_pagamento == "Pix" else "Pendente"

        novo_agendamento = Agendamento(
            cliente_id=current_user.id,
            barbeiro_id=int(barbeiro_id),
            servico_id=int(servico_id),
            data=data_obj,
            horario=horario_obj,
            forma_pagamento=forma_pagamento,
            status_pagamento=status_pagamento
        )

        try:
            db.session.add(novo_agendamento)
            db.session.commit()
            flash("Agendamento realizado com sucesso!")
        except IntegrityError:
            db.session.rollback()
            flash("Erro ao salvar agendamento.")

        return redirect(url_for("agendamento"))

    # 🔥 FILTRO DE AGENDAMENTOS (remove após 1h)
    agora = datetime.now()

    agendamentos = (
        Agendamento.query
        .filter(Agendamento.cliente_id == current_user.id)
        .all()
    )

    agendamentos = [
        ag for ag in agendamentos
        if datetime.combine(ag.data, ag.horario) + timedelta(hours=1) > agora
    ]

    agendamentos.sort(key=lambda x: (x.data, x.horario))

    return render_template(
        "agendamento.html",
        barbeiros=barbeiros,
        servicos=servicos,
        agendamentos=agendamentos
    )


# ---------------- CANCELAR AGENDAMENTO ----------------
@app.route("/cancelar-agendamento/<int:id>", methods=["POST"])
@login_required
def cancelar_agendamento(id):
    agendamento = Agendamento.query.get_or_404(id)

    if agendamento.cliente_id != current_user.id:
        return "Não autorizado", 403

    agora = datetime.now()
    data_hora_agendamento = datetime.combine(
        agendamento.data,
        agendamento.horario
    )

    if data_hora_agendamento - agora < timedelta(hours=3):
        return jsonify({"erro": "Só pode cancelar com 3h de antecedência"}), 400

    db.session.delete(agendamento)
    db.session.commit()

    return jsonify({"success": True})


# ---------------- LOGOUT ----------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da sua conta com sucesso!')
    return redirect(url_for('index'))


# ==========================================
# START
# ==========================================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
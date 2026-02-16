from flask import Flask, render_template, redirect, url_for, request, flash
from config import Config
from models import db, Usuario, Barbeiro, Agendamento
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, time

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

HORARIO_ABERTURA = 9
HORARIO_FECHAMENTO = 19

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# ---------------- HOME ----------------
@app.route("/")
def index():
    return render_template("index.html")

# ---------------- REGISTRO ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = generate_password_hash(request.form["senha"])

        novo = Usuario(nome=nome, email=email, senha=senha)
        db.session.add(novo)
        db.session.commit()

        flash("Cadastro realizado com sucesso!")
        return redirect(url_for("login"))

    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        user = Usuario.query.filter_by(email=email).first()

        if user and check_password_hash(user.senha, senha):
            login_user(user)
            return redirect(url_for("index"))
        else:
            flash("Login inválido")

    return render_template("login.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

# ---------------- AGENDAMENTO ----------------
@app.route("/agendamento", methods=["GET", "POST"])
@login_required
def agendamento():
    barbeiros = Barbeiro.query.all()

    if request.method == "POST":
        barbeiro_id = request.form["barbeiro"]
        data = datetime.strptime(request.form["data"], "%Y-%m-%d").date()
        horario = datetime.strptime(request.form["horario"], "%H:%M").time()

        # Verifica horário funcionamento
        if horario.hour < HORARIO_ABERTURA or horario.hour >= HORARIO_FECHAMENTO:
            flash("Fora do horário de funcionamento")
            return redirect(url_for("agendamento"))

        # Verifica duplicidade
        conflito = Agendamento.query.filter_by(
            barbeiro_id=barbeiro_id,
            data=data,
            horario=horario
        ).first()

        if conflito:
            flash("Horário já agendado")
            return redirect(url_for("agendamento"))

        novo = Agendamento(
            cliente_id=current_user.id,
            barbeiro_id=barbeiro_id,
            data=data,
            horario=horario
        )

        db.session.add(novo)
        db.session.commit()

        flash("Agendamento realizado com sucesso!")
        return redirect(url_for("index"))

    return render_template("agendamento.html", barbeiros=barbeiros)

# ---------------- ADMIN ----------------
@app.route("/admin")
@login_required
def admin():
    if not current_user.is_admin:
        return redirect(url_for("index"))

    agendamentos = Agendamento.query.all()
    return render_template("admin.html", agendamentos=agendamentos)

# ---------------- CRIAR BANCO ----------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

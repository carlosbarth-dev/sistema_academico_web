import os
from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for
from pg8000.dbapi import DatabaseError
from werkzeug.security import check_password_hash

from database import inicializar_banco
from repositories import (
    boletim_aluno,
    buscar_aluno,
    buscar_usuario_por_login,
    criar_aluno,
    criar_turma,
    criar_usuarios_padrao,
    lancar_nota,
    listar_alunos,
    listar_turmas,
    remover_aluno,
    resumo_dashboard,
)


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "chave-dev-sistema-academico")


# Anotacao minha:
# Eu uso session para lembrar quem fez login.
# Assim o usuario nao precisa mandar login e senha em cada formulario.

def usuario_logado():
    return session.get("usuario")


def login_obrigatorio(funcao):
    @wraps(funcao)
    def wrapper(*args, **kwargs):
        if not usuario_logado():
            flash("Faca login para acessar o sistema.", "erro")
            return redirect(url_for("login"))
        return funcao(*args, **kwargs)

    return wrapper


def perfis_permitidos(*perfis):
    def decorador(funcao):
        @wraps(funcao)
        def wrapper(*args, **kwargs):
            usuario = usuario_logado()

            if not usuario or usuario["perfil"] not in perfis:
                flash("Seu perfil nao tem permissao para essa acao.", "erro")
                return redirect(url_for("index"))

            return funcao(*args, **kwargs)

        return wrapper

    return decorador


def pode(*perfis):
    usuario = usuario_logado()
    return bool(usuario and usuario["perfil"] in perfis)


def situacao_por_media(media):
    if media is None:
        return "Sem notas", "recuperacao"
    if media >= 7:
        return "Aprovado", "aprovado"
    if media >= 5:
        return "Recuperacao", "recuperacao"
    return "Reprovado", "reprovado"


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_digitado = request.form["login"].strip()
        senha_digitada = request.form["senha"].strip()
        usuario = buscar_usuario_por_login(login_digitado)

        if usuario and check_password_hash(usuario["senha_hash"], senha_digitada):
            session["usuario"] = {
                "id": usuario["id"],
                "nome": usuario["nome"],
                "login": usuario["login"],
                "perfil": usuario["perfil"],
            }
            flash("Login realizado com sucesso.", "sucesso")
            return redirect(url_for("index"))

        flash("Login ou senha invalidos.", "erro")

    return render_template("login.html")


@app.get("/logout")
def logout():
    session.clear()
    flash("Voce saiu do sistema.", "sucesso")
    return redirect(url_for("login"))


@app.route("/")
@login_obrigatorio
def index():
    busca = request.args.get("busca", "").strip()
    aluno_id = request.args.get("aluno_id", type=int)

    alunos = listar_alunos(busca)
    turmas = listar_turmas()
    resumo = resumo_dashboard()
    aluno_selecionado = buscar_aluno(aluno_id) if aluno_id else None
    boletim = boletim_aluno(aluno_id) if aluno_id else []

    for aluno in alunos:
        texto, classe = situacao_por_media(aluno["media"])
        aluno["situacao_texto"] = texto
        aluno["situacao_classe"] = classe

    return render_template(
        "index.html",
        alunos=alunos,
        turmas=turmas,
        resumo=resumo,
        busca=busca,
        aluno_selecionado=aluno_selecionado,
        boletim=boletim,
        usuario=usuario_logado(),
        pode=pode,
    )


@app.post("/turmas")
@login_obrigatorio
@perfis_permitidos("admin", "secretaria")
def salvar_turma():
    try:
        criar_turma(
            request.form["nome"].strip(),
            request.form["turno"].strip(),
        )
        flash("Turma salva com sucesso.", "sucesso")
    except DatabaseError as erro:
        flash(f"Erro ao salvar turma: {erro}", "erro")

    return redirect(url_for("index"))


@app.post("/alunos")
@login_obrigatorio
@perfis_permitidos("admin", "secretaria")
def salvar_aluno():
    try:
        criar_aluno(
            request.form["nome"].strip(),
            request.form["matricula"].strip(),
            request.form["cpf"].strip(),
            request.form["telefone"].strip(),
            request.form["email"].strip(),
            request.form["data_nascimento"].strip(),
            int(request.form["turma_id"]),
        )
        flash("Aluno cadastrado com sucesso.", "sucesso")
    except DatabaseError as erro:
        flash(f"Erro ao cadastrar aluno: {erro}", "erro")

    return redirect(url_for("index"))


@app.post("/notas")
@login_obrigatorio
@perfis_permitidos("admin", "professor")
def salvar_nota():
    try:
        lancar_nota(
            int(request.form["aluno_id"]),
            request.form["disciplina"].strip(),
            float(request.form["nota1"]),
            float(request.form["nota2"]),
        )
        flash("Nota lancada com sucesso.", "sucesso")
    except DatabaseError as erro:
        flash(f"Erro ao lancar nota: {erro}", "erro")

    return redirect(url_for("index", aluno_id=request.form["aluno_id"]))


@app.post("/alunos/<int:aluno_id>/remover")
@login_obrigatorio
@perfis_permitidos("admin", "secretaria")
def excluir_aluno(aluno_id):
    remover_aluno(aluno_id)
    flash("Aluno removido com sucesso.", "sucesso")
    return redirect(url_for("index"))


if __name__ == "__main__":
    # Anotacao minha:
    # Eu inicializo o banco e crio usuarios padrao antes de abrir o site.
    # Isso garante que eu consiga entrar no sistema logo no primeiro uso.
    inicializar_banco()
    criar_usuarios_padrao()
    app.run(debug=True)

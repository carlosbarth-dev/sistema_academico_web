import os

from flask import Flask, flash, redirect, render_template, request, url_for
from psycopg2 import Error as PostgresError

from database import inicializar_banco
from repositories import (
    boletim_aluno,
    buscar_aluno,
    criar_aluno,
    criar_turma,
    lancar_nota,
    listar_alunos,
    listar_turmas,
    remover_aluno,
    resumo_dashboard,
)


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "chave-dev-sistema-academico")


def situacao_por_media(media):
    if media is None:
        return "Sem notas", "recuperacao"
    if media >= 7:
        return "Aprovado", "aprovado"
    if media >= 5:
        return "Recuperacao", "recuperacao"
    return "Reprovado", "reprovado"


@app.route("/")
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
    )


@app.post("/turmas")
def salvar_turma():
    try:
        criar_turma(
            request.form["nome"].strip(),
            request.form["turno"].strip(),
        )
        flash("Turma salva com sucesso.", "sucesso")
    except PostgresError as erro:
        flash(f"Erro ao salvar turma: {erro}", "erro")

    return redirect(url_for("index"))


@app.post("/alunos")
def salvar_aluno():
    try:
        criar_aluno(
            request.form["nome"].strip(),
            request.form["matricula"].strip(),
            int(request.form["turma_id"]),
        )
        flash("Aluno cadastrado com sucesso.", "sucesso")
    except PostgresError as erro:
        flash(f"Erro ao cadastrar aluno: {erro}", "erro")

    return redirect(url_for("index"))


@app.post("/notas")
def salvar_nota():
    try:
        lancar_nota(
            int(request.form["aluno_id"]),
            request.form["disciplina"].strip(),
            float(request.form["nota1"]),
            float(request.form["nota2"]),
        )
        flash("Nota lancada com sucesso.", "sucesso")
    except PostgresError as erro:
        flash(f"Erro ao lancar nota: {erro}", "erro")

    return redirect(url_for("index", aluno_id=request.form["aluno_id"]))


@app.post("/alunos/<int:aluno_id>/remover")
def excluir_aluno(aluno_id):
    remover_aluno(aluno_id)
    flash("Aluno removido com sucesso.", "sucesso")
    return redirect(url_for("index"))


if __name__ == "__main__":
    # Eu inicializo o banco antes de subir o servidor para garantir que as tabelas existam.
    inicializar_banco()
    app.run(debug=True)

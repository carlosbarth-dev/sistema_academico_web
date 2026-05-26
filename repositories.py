from werkzeug.security import generate_password_hash

from database import execute, fetch_all, fetch_one


# Anotacao minha:
# Eu deixei este arquivo apenas para comandos de banco.
# Assim o app.py cuida das rotas e este arquivo cuida do SQL.


def listar_turmas():
    return fetch_all(
        """
        SELECT id, nome, turno
          FROM turmas
         ORDER BY nome
        """
    )


def criar_turma(nome, turno):
    return execute(
        """
        INSERT INTO turmas (nome, turno)
        VALUES (%s, %s)
        ON CONFLICT (nome)
        DO UPDATE SET turno = EXCLUDED.turno
        RETURNING id
        """,
        (nome, turno),
    )


def listar_alunos(busca=""):
    termo = f"%{busca}%"
    return fetch_all(
        """
        SELECT
            a.id,
            a.nome,
            a.matricula,
            a.cpf,
            a.telefone,
            a.email,
            a.data_nascimento,
            t.nome AS turma,
            ROUND(AVG(n.media), 2) AS media
          FROM alunos a
          JOIN turmas t ON t.id = a.turma_id
          LEFT JOIN notas n ON n.aluno_id = a.id
         WHERE a.nome ILIKE %s
            OR a.matricula ILIKE %s
            OR COALESCE(a.cpf, '') ILIKE %s
            OR COALESCE(a.email, '') ILIKE %s
         GROUP BY a.id, a.nome, a.matricula, a.cpf, a.telefone, a.email, a.data_nascimento, t.nome
         ORDER BY a.nome
        """,
        (termo, termo, termo, termo),
    )


def criar_aluno(nome, matricula, cpf, telefone, email, data_nascimento, turma_id):
    return execute(
        """
        INSERT INTO alunos (nome, matricula, cpf, telefone, email, data_nascimento, turma_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (nome, matricula, cpf, telefone, email, data_nascimento or None, turma_id),
    )


def remover_aluno(aluno_id):
    execute("DELETE FROM alunos WHERE id = %s", (aluno_id,))


def buscar_aluno(aluno_id):
    return fetch_one(
        """
        SELECT
            a.id,
            a.nome,
            a.matricula,
            a.cpf,
            a.telefone,
            a.email,
            a.data_nascimento,
            t.nome AS turma
          FROM alunos a
          JOIN turmas t ON t.id = a.turma_id
         WHERE a.id = %s
        """,
        (aluno_id,),
    )


def buscar_ou_criar_disciplina(nome):
    disciplina = execute(
        """
        INSERT INTO disciplinas (nome)
        VALUES (%s)
        ON CONFLICT (nome)
        DO UPDATE SET nome = EXCLUDED.nome
        RETURNING id
        """,
        (nome,),
    )

    return disciplina["id"]


def lancar_nota(aluno_id, disciplina, nota1, nota2):
    disciplina_id = buscar_ou_criar_disciplina(disciplina)
    media = (nota1 + nota2) / 2

    execute(
        """
        INSERT INTO notas (aluno_id, disciplina_id, nota1, nota2, media)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (aluno_id, disciplina_id)
        DO UPDATE SET
            nota1 = EXCLUDED.nota1,
            nota2 = EXCLUDED.nota2,
            media = EXCLUDED.media,
            atualizado_em = CURRENT_TIMESTAMP
        """,
        (aluno_id, disciplina_id, nota1, nota2, media),
    )


def boletim_aluno(aluno_id):
    return fetch_all(
        """
        SELECT
            d.nome AS disciplina,
            n.nota1,
            n.nota2,
            n.media
          FROM notas n
          JOIN disciplinas d ON d.id = n.disciplina_id
         WHERE n.aluno_id = %s
         ORDER BY d.nome
        """,
        (aluno_id,),
    )


def resumo_dashboard():
    return fetch_one(
        """
        WITH medias_alunos AS (
            SELECT aluno_id, AVG(media) AS media_geral
              FROM notas
             GROUP BY aluno_id
        )
        SELECT
            (SELECT COUNT(*) FROM alunos) AS total_alunos,
            (SELECT COUNT(*) FROM turmas) AS total_turmas,
            COUNT(*) FILTER (WHERE media_geral >= 7) AS total_aprovados,
            COALESCE(ROUND(AVG(media_geral), 2), 0) AS media_geral
          FROM medias_alunos
        """
    )


def buscar_usuario_por_login(login):
    return fetch_one(
        """
        SELECT id, nome, login, senha_hash, perfil, professor_id
          FROM usuarios
         WHERE login = %s
           AND ativo = TRUE
        """,
        (login,),
    )


def criar_usuario_padrao(nome, login, senha, perfil, professor_id=None):
    # Anotacao minha:
    # Eu nunca salvo senha pura no banco. Primeiro transformo em hash.
    # Assim, mesmo olhando a tabela usuarios no pgAdmin4, a senha nao aparece aberta.
    execute(
        """
        INSERT INTO usuarios (nome, login, senha_hash, perfil, professor_id)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (login) DO NOTHING
        """,
        (nome, login, generate_password_hash(senha), perfil, professor_id),
    )


def professor_padrao():
    return fetch_one("SELECT id FROM professores WHERE email = %s", ("mariana.prof@example.com",))


def criar_usuarios_padrao():
    professora = professor_padrao()
    professora_id = professora["id"] if professora else None

    criar_usuario_padrao("Administrador", "admin", "admin123", "admin")
    criar_usuario_padrao("Secretaria", "secretaria", "secretaria123", "secretaria")
    criar_usuario_padrao("Mariana Souza", "professor", "professor123", "professor", professora_id)

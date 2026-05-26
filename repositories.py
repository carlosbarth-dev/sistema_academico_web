from database import execute, fetch_all, fetch_one


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
            t.nome AS turma,
            ROUND(AVG(n.media), 2) AS media
          FROM alunos a
          JOIN turmas t ON t.id = a.turma_id
          LEFT JOIN notas n ON n.aluno_id = a.id
         WHERE a.nome ILIKE %s
            OR a.matricula ILIKE %s
         GROUP BY a.id, a.nome, a.matricula, t.nome
         ORDER BY a.nome
        """,
        (termo, termo),
    )


def criar_aluno(nome, matricula, turma_id):
    return execute(
        """
        INSERT INTO alunos (nome, matricula, turma_id)
        VALUES (%s, %s, %s)
        RETURNING id
        """,
        (nome, matricula, turma_id),
    )


def remover_aluno(aluno_id):
    execute("DELETE FROM alunos WHERE id = %s", (aluno_id,))


def buscar_aluno(aluno_id):
    return fetch_one(
        """
        SELECT a.id, a.nome, a.matricula, t.nome AS turma
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

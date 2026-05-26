CREATE TABLE IF NOT EXISTS turmas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(80) NOT NULL UNIQUE,
    turno VARCHAR(20) NOT NULL,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS alunos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    matricula VARCHAR(30) NOT NULL UNIQUE,
    turma_id INTEGER NOT NULL,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_alunos_turma
        FOREIGN KEY (turma_id)
        REFERENCES turmas(id)
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS disciplinas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(120) NOT NULL UNIQUE,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notas (
    id SERIAL PRIMARY KEY,
    aluno_id INTEGER NOT NULL,
    disciplina_id INTEGER NOT NULL,
    nota1 NUMERIC(4, 2) NOT NULL CHECK (nota1 >= 0 AND nota1 <= 10),
    nota2 NUMERIC(4, 2) NOT NULL CHECK (nota2 >= 0 AND nota2 <= 10),
    media NUMERIC(4, 2) NOT NULL CHECK (media >= 0 AND media <= 10),
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_nota_aluno_disciplina UNIQUE (aluno_id, disciplina_id),
    CONSTRAINT fk_notas_aluno
        FOREIGN KEY (aluno_id)
        REFERENCES alunos(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_notas_disciplina
        FOREIGN KEY (disciplina_id)
        REFERENCES disciplinas(id)
        ON DELETE CASCADE
);

INSERT INTO turmas (nome, turno)
VALUES
    ('ADS 1', 'Noite'),
    ('Informatica 2', 'Manha')
ON CONFLICT (nome) DO NOTHING;

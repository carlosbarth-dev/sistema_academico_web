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
    cpf VARCHAR(14) UNIQUE,
    telefone VARCHAR(20),
    email VARCHAR(120),
    data_nascimento DATE,
    turma_id INTEGER NOT NULL,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_alunos_turma
        FOREIGN KEY (turma_id)
        REFERENCES turmas(id)
        ON DELETE RESTRICT
);

ALTER TABLE alunos ADD COLUMN IF NOT EXISTS cpf VARCHAR(14);
ALTER TABLE alunos ADD COLUMN IF NOT EXISTS telefone VARCHAR(20);
ALTER TABLE alunos ADD COLUMN IF NOT EXISTS email VARCHAR(120);
ALTER TABLE alunos ADD COLUMN IF NOT EXISTS data_nascimento DATE;

CREATE TABLE IF NOT EXISTS professores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    cpf VARCHAR(14) UNIQUE,
    telefone VARCHAR(20),
    email VARCHAR(120) UNIQUE,
    area VARCHAR(120) NOT NULL,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    login VARCHAR(60) NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    perfil VARCHAR(20) NOT NULL CHECK (perfil IN ('admin', 'secretaria', 'professor')),
    professor_id INTEGER,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_usuarios_professor
        FOREIGN KEY (professor_id)
        REFERENCES professores(id)
        ON DELETE SET NULL
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

INSERT INTO professores (nome, cpf, telefone, email, area)
VALUES
    ('Mariana Souza', '111.222.333-44', '(11) 98888-1111', 'mariana.prof@example.com', 'Programacao')
ON CONFLICT (email) DO NOTHING;

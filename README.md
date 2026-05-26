# Sistema Academico Web

Projeto web feito com **Python, Flask e PostgreSQL** para cadastrar alunos, turmas e notas.

Eu organizei este sistema para praticar uma aplicacao mais parecida com um projeto real:

- a interface fica no navegador;
- o Flask recebe os formularios;
- o PostgreSQL guarda os dados;
- o pgAdmin4 pode ser usado para visualizar as tabelas;
- o SQL fica separado em `schema.sql`;
- as operacoes do banco ficam em `repositories.py`;
- a conexao fica centralizada em `database.py`.

## Funcionalidades

- Cadastro de turmas
- Cadastro de alunos
- Lancamento de notas por disciplina
- Atualizacao automatica da nota caso o aluno ja tenha nota naquela disciplina
- Consulta de boletim
- Calculo de media
- Situacao do aluno: aprovado, recuperacao ou reprovado
- Busca de aluno por nome ou matricula
- Remocao de aluno
- Dashboard com totais do sistema

## Tecnologias

- Python 3
- Flask
- PostgreSQL
- pgAdmin4
- psycopg2
- HTML
- CSS

## Estrutura do projeto

```text
sistema_academico_web
|
|-- app.py
|-- database.py
|-- repositories.py
|-- schema.sql
|-- requirements.txt
|-- .env.example
|-- templates/
|   |-- index.html
|-- static/
|   |-- styles.css
|-- README.md
```

## Explicacao dos arquivos

### app.py

Arquivo principal do sistema.

Anotacao minha:
Eu deixei o `app.py` responsavel pelas rotas do site. Ele recebe os dados dos formularios, chama as funcoes do banco e devolve a pagina atualizada para o navegador.

### database.py

Arquivo responsavel pela conexao com o PostgreSQL.

Anotacao minha:
Eu separei a conexao para nao repetir codigo em varios lugares. Tambem deixei o sistema criar o banco automaticamente se ele ainda nao existir.

### repositories.py

Arquivo com as operacoes SQL do sistema.

Anotacao minha:
Aqui eu deixei os comandos de cadastro, listagem, remocao, boletim e resumo. Assim o `app.py` nao fica misturado com muito SQL.

### schema.sql

Arquivo com a modelagem do banco.

Anotacao minha:
Eu deixei as tabelas em um arquivo separado porque fica mais facil abrir no pgAdmin4, estudar a estrutura e entender os relacionamentos.

## Modelagem do banco

O banco se chama:

```text
sistema_academico_web
```

Tabelas principais:

- `turmas`
- `alunos`
- `disciplinas`
- `notas`

Relacionamentos:

- Uma turma pode ter varios alunos.
- Um aluno pertence a uma turma.
- Uma disciplina pode aparecer em varias notas.
- Uma nota pertence a um aluno e a uma disciplina.
- Se um aluno for removido, as notas dele tambem sao removidas.

## Como configurar o banco no pgAdmin4

### 1. Abrir o pgAdmin4

Abra o pgAdmin4 e conecte no seu servidor PostgreSQL.

Normalmente o servidor fica em:

```text
localhost
```

Porta padrao:

```text
5432
```

Usuario comum:

```text
postgres
```

### 2. Criar o banco manualmente, se quiser

O sistema consegue criar o banco sozinho, mas voce tambem pode criar pelo pgAdmin4:

```sql
CREATE DATABASE sistema_academico_web;
```

### 3. Conferir as tabelas

Depois de executar o sistema pela primeira vez, abra no pgAdmin4:

```text
Servers > PostgreSQL > Databases > sistema_academico_web > Schemas > public > Tables
```

Ali devem aparecer:

- `alunos`
- `disciplinas`
- `notas`
- `turmas`

## Como executar o projeto

### 1. Entrar na pasta do projeto

```powershell
cd C:\Users\Kingottahoo\Desktop\sistema_academico_web
```

### 2. Criar ambiente virtual

```powershell
py -m venv .venv
```

### 3. Ativar ambiente virtual

```powershell
.\.venv\Scripts\activate
```

### 4. Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 5. Criar arquivo `.env`

Copie o arquivo `.env.example` e crie um arquivo chamado `.env`.

Exemplo:

```text
PGHOST=localhost
PGPORT=5432
PGUSER=postgres
PGPASSWORD=sua_senha_do_postgres
PGDATABASE=sistema_academico_web
FLASK_SECRET_KEY=uma_chave_qualquer
```

Anotacao minha:
Eu deixei a senha fora do codigo para nao subir senha pessoal para o GitHub.

### 6. Rodar o sistema

```powershell
py app.py
```

Depois abra no navegador:

```text
http://127.0.0.1:5000
```

## Observacoes importantes

- O sistema usa PostgreSQL, que pode ser acompanhado pelo pgAdmin4.
- O pgAdmin4 nao e o banco em si; ele e a ferramenta visual para administrar o PostgreSQL.
- As tabelas sao criadas automaticamente quando o `app.py` e executado.
- O arquivo `.env` nao deve ir para o GitHub porque pode conter senha do banco.

## Autor

Desenvolvido por Carlos Barth.

Estudante de Analise e Desenvolvimento de Sistemas.

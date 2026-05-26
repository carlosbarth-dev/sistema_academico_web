const CHAVE_DADOS = "sistema_academico_web";

let estado = carregarDados();

const formAluno = document.querySelector("#formAluno");
const formTurma = document.querySelector("#formTurma");
const formNota = document.querySelector("#formNota");
const turmaAluno = document.querySelector("#turmaAluno");
const alunoNota = document.querySelector("#alunoNota");
const listaAlunos = document.querySelector("#listaAlunos");
const boletim = document.querySelector("#boletim");
const buscaAluno = document.querySelector("#buscaAluno");

function gerarId() {
    return Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
}

function carregarDados() {
    const salvo = localStorage.getItem(CHAVE_DADOS);

    if (salvo) {
        return JSON.parse(salvo);
    }

    return criarEstadoInicial();
}

function criarEstadoInicial() {
    return {
        turmas: [
            { id: gerarId(), nome: "ADS 1", turno: "Noite" },
            { id: gerarId(), nome: "Informatica 2", turno: "Manha" }
        ],
        alunos: [],
        notas: []
    };
}

function salvarDados() {
    localStorage.setItem(CHAVE_DADOS, JSON.stringify(estado));
}

function calcularMedia(alunoId) {
    const notasAluno = estado.notas.filter((nota) => nota.alunoId === alunoId);

    if (notasAluno.length === 0) {
        return null;
    }

    const soma = notasAluno.reduce((total, nota) => total + nota.media, 0);
    return soma / notasAluno.length;
}

function obterSituacao(media) {
    if (media === null) {
        return { texto: "Sem notas", classe: "recuperacao" };
    }

    if (media >= 7) {
        return { texto: "Aprovado", classe: "aprovado" };
    }

    if (media >= 5) {
        return { texto: "Recuperacao", classe: "recuperacao" };
    }

    return { texto: "Reprovado", classe: "reprovado" };
}

function buscarTurma(id) {
    return estado.turmas.find((turma) => turma.id === id);
}

function atualizarResumo() {
    const medias = estado.alunos
        .map((aluno) => calcularMedia(aluno.id))
        .filter((media) => media !== null);

    const aprovados = medias.filter((media) => media >= 7).length;
    const mediaGeral = medias.length
        ? medias.reduce((total, media) => total + media, 0) / medias.length
        : 0;

    document.querySelector("#totalAlunos").textContent = estado.alunos.length;
    document.querySelector("#totalTurmas").textContent = estado.turmas.length;
    document.querySelector("#totalAprovados").textContent = aprovados;
    document.querySelector("#mediaGeral").textContent = mediaGeral.toFixed(1);
}

function atualizarSelects() {
    turmaAluno.innerHTML = "";
    alunoNota.innerHTML = "";

    estado.turmas.forEach((turma) => {
        const option = document.createElement("option");
        option.value = turma.id;
        option.textContent = `${turma.nome} - ${turma.turno}`;
        turmaAluno.appendChild(option);
    });

    estado.alunos.forEach((aluno) => {
        const option = document.createElement("option");
        option.value = aluno.id;
        option.textContent = aluno.nome;
        alunoNota.appendChild(option);
    });
}

function renderizarAlunos() {
    const termo = buscaAluno.value.trim().toLowerCase();
    const alunosFiltrados = estado.alunos.filter((aluno) => {
        return aluno.nome.toLowerCase().includes(termo)
            || aluno.matricula.toLowerCase().includes(termo);
    });

    listaAlunos.innerHTML = "";

    if (alunosFiltrados.length === 0) {
        listaAlunos.innerHTML = `
            <tr>
                <td colspan="6">Nenhum aluno encontrado.</td>
            </tr>
        `;
        return;
    }

    alunosFiltrados.forEach((aluno) => {
        const turma = buscarTurma(aluno.turmaId);
        const media = calcularMedia(aluno.id);
        const situacao = obterSituacao(media);
        const linha = document.createElement("tr");

        linha.innerHTML = `
            <td>${aluno.nome}</td>
            <td>${aluno.matricula}</td>
            <td>${turma ? turma.nome : "Sem turma"}</td>
            <td>${media === null ? "-" : media.toFixed(1)}</td>
            <td><span class="situacao ${situacao.classe}">${situacao.texto}</span></td>
            <td class="acoes">
                <button type="button" data-boletim="${aluno.id}">Boletim</button>
                <button class="botao-perigo" type="button" data-remover="${aluno.id}">Remover</button>
            </td>
        `;

        listaAlunos.appendChild(linha);
    });
}

function renderizarBoletim(alunoId) {
    const aluno = estado.alunos.find((item) => item.id === alunoId);

    if (!aluno) {
        boletim.className = "boletim vazio";
        boletim.textContent = "Selecione um aluno na tabela para visualizar o boletim.";
        return;
    }

    const notasAluno = estado.notas.filter((nota) => nota.alunoId === alunoId);
    const media = calcularMedia(alunoId);
    const situacao = obterSituacao(media);

    boletim.className = "boletim";
    boletim.innerHTML = `
        <strong>${aluno.nome}</strong>
        <p>Matricula: ${aluno.matricula}</p>
        <p>Media geral: ${media === null ? "Sem notas" : media.toFixed(1)}</p>
        <p>Situacao: ${situacao.texto}</p>
        <ul>
            ${notasAluno.map((nota) => `
                <li>${nota.disciplina}: ${nota.nota1.toFixed(1)} e ${nota.nota2.toFixed(1)} - media ${nota.media.toFixed(1)}</li>
            `).join("") || "<li>Nenhuma nota cadastrada.</li>"}
        </ul>
    `;
}

function renderizarTudo() {
    atualizarResumo();
    atualizarSelects();
    renderizarAlunos();
}

formTurma.addEventListener("submit", (evento) => {
    evento.preventDefault();

    estado.turmas.push({
        id: gerarId(),
        nome: document.querySelector("#nomeTurma").value.trim(),
        turno: document.querySelector("#turnoTurma").value
    });

    formTurma.reset();
    salvarDados();
    renderizarTudo();
});

formAluno.addEventListener("submit", (evento) => {
    evento.preventDefault();

    estado.alunos.push({
        id: gerarId(),
        nome: document.querySelector("#nomeAluno").value.trim(),
        matricula: document.querySelector("#matriculaAluno").value.trim(),
        turmaId: turmaAluno.value
    });

    formAluno.reset();
    salvarDados();
    renderizarTudo();
});

formNota.addEventListener("submit", (evento) => {
    evento.preventDefault();

    const nota1 = Number(document.querySelector("#nota1").value);
    const nota2 = Number(document.querySelector("#nota2").value);

    estado.notas.push({
        id: gerarId(),
        alunoId: alunoNota.value,
        disciplina: document.querySelector("#disciplinaNota").value.trim(),
        nota1,
        nota2,
        media: (nota1 + nota2) / 2
    });

    formNota.reset();
    salvarDados();
    renderizarTudo();
});

listaAlunos.addEventListener("click", (evento) => {
    const alunoBoletim = evento.target.dataset.boletim;
    const alunoRemover = evento.target.dataset.remover;

    if (alunoBoletim) {
        renderizarBoletim(alunoBoletim);
    }

    if (alunoRemover) {
        estado.alunos = estado.alunos.filter((aluno) => aluno.id !== alunoRemover);
        estado.notas = estado.notas.filter((nota) => nota.alunoId !== alunoRemover);
        salvarDados();
        renderizarTudo();
        renderizarBoletim(null);
    }
});

buscaAluno.addEventListener("input", renderizarAlunos);

document.querySelector("#limparDados").addEventListener("click", () => {
    if (confirm("Deseja apagar todos os dados cadastrados?")) {
        localStorage.removeItem(CHAVE_DADOS);
        estado = carregarDados();
        renderizarTudo();
        renderizarBoletim(null);
    }
});

renderizarTudo();

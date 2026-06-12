// ================================
// ===== SELEÇÃO DE ELEMENTOS =====
// ================================
const fileInput = document.getElementById("file");
const previewArea = document.getElementById("preview-area");
const processBtn = document.getElementById("process-btn");
const nextBtn = document.getElementById("next-page");
const prevBtn = document.getElementById("prev-page");
const themeToggle = document.getElementById("theme-toggle");
const resultsDiv = document.getElementById("results");
const fileName = document.getElementById("file-name");

// =============================
// ===== VARIÁVEIS GLOBAIS =====
// =============================
let pdfFile = null;
let fileType = "";
let currentPage = 1;

// ===============================
// ===== TEMA CLARO / ESCURO =====
// ===============================
// Aplicar tema salvo ao carregar página
document.addEventListener("DOMContentLoaded", () => {
  const temaSalvo = localStorage.getItem("tema");

  if (temaSalvo === "dark") {
    document.body.classList.add("dark");
    themeToggle.textContent = "☀️ Modo Claro";
  }
});

// Alternar tema ao clicar
themeToggle.addEventListener("click", () => {

  document.body.classList.toggle("dark");

  if (document.body.classList.contains("dark")) {
    themeToggle.textContent = "☀️ Modo Claro";
    localStorage.setItem("tema", "dark");  // salva
  } else {
    themeToggle.textContent = "🌙 Modo Escuro";
    localStorage.setItem("tema", "light"); // salva
  }
});

// ==============================
// ===== PREVIEW DO ARQUIVO =====
// ==============================
fileInput.addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (!file) return;

  fileName.textContent = file.name;

  pdfFile = URL.createObjectURL(file);
  fileType = file.type;
  previewArea.innerHTML = "";

  // ===== PREVIEW PDF =====
  if (fileType.includes("pdf")) {
    const iframe = document.createElement("iframe");
    iframe.src = pdfFile + "#page=1";
    iframe.width = "100%";
    iframe.height = "700";
    previewArea.appendChild(iframe);
    nextBtn.disabled = false;

  // ===== PREVIEW IMAGEM =====
  } else if (fileType.includes("image")) {
    const img = document.createElement("img");
    img.src = pdfFile;
    previewArea.appendChild(img);
    nextBtn.disabled = true;

  // ===== FORMATO NÃO SUPORTADO =====
  } else {
    previewArea.innerHTML = "<p>Formato não suportado para preview.</p>";
    nextBtn.disabled = true;
  }
});

// ======================================
// ===== PROCESSAMENTO DO DOCUMENTO =====
// ======================================
processBtn.addEventListener("click", async () => {

  const file = fileInput.files[0];

  // ===== VALIDAÇÃO =====
  if (!file) {
    alert("Selecione um arquivo primeiro!");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  resultsDiv.innerHTML = "<p>Processando...</p>";

  try {
    const response = await fetch("/processar", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (data.sucesso) {

      resultsDiv.innerHTML = "";

      // ================================
      // ===== RESULTADOS EXTRAÍDOS =====
      // ================================
      if (data.resultados && data.resultados.length > 0) {

        data.resultados.forEach((item, index) => {

          const div = document.createElement("div");
          div.classList.add("result-item");

          const titulo = document.createElement("h4");
          titulo.textContent = `Resultado ${index + 1}`;
          div.appendChild(titulo);

          for (const [chave, valor] of Object.entries(item)) {
            const linha = document.createElement("p");
            linha.innerHTML = `<strong>${chave}:</strong> ${valor}`;
            div.appendChild(linha);
          }

          resultsDiv.appendChild(div);
        });
      }

      // ===================================
      // ===== RESUMO DE PROCESSAMENTO =====
      // ===================================
      const resumoBox = document.createElement("div");
      resumoBox.classList.add("summary-box");

      const totalPaginas = data.total_paginas || 0;
      const paginasNaoCapturadas = data.paginas_nao_capturadas || [];

      let taxaSucesso = 0;

      if (totalPaginas > 0) {
        taxaSucesso = (
          ((totalPaginas - paginasNaoCapturadas.length) / totalPaginas) * 100
        ).toFixed(1);
      }

      resumoBox.innerHTML = `
        <hr>
        <h3>Resumo do Processamento</h3>
        <p><strong>Total de páginas:</strong> ${totalPaginas}</p>
        <p><strong>Páginas não capturadas:</strong> ${paginasNaoCapturadas.length}</p>
        <p><strong>Taxa de sucesso:</strong> ${taxaSucesso}%</p>
      `;

      // ===========================================
      // ===== LISTA DE PÁGINAS NÃO CAPTURADAS =====
      // ===========================================
      if (paginasNaoCapturadas.length > 0) {
        const aviso = document.createElement("div");
        aviso.style.color = "orange";
        aviso.innerHTML = `
          <strong>Páginas sem extração:</strong> 
          ${paginasNaoCapturadas.join(", ")}
        `;
        resumoBox.appendChild(aviso);
      }

      resultsDiv.appendChild(resumoBox);

    } else {
      resultsDiv.innerHTML = `<p style="color:red;">Erro: ${data.mensagem}</p>`;
    }

  } catch (error) {
    resultsDiv.innerHTML = `<p style="color:red;">Erro na comunicação com o servidor.</p>`;
  }
});
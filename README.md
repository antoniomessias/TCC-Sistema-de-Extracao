# 📄 Sistema de Extração e Análise Multi Formato de Documentos

> Trabalho de Conclusão de Curso — Análise e Desenvolvimento de Sistemas  
> Instituto Federal de Educação, Ciência e Tecnologia de São Paulo — Campus Campinas (IFSP)  
> **Autores:** Antonio Messias Ferreira da Silva · Luiz Henrique Nunes Santana  
> **Orientador:** Prof. Dr. Ricardo Barz Sovat

---

## 📌 Sobre o Projeto

Este projeto é um aplicativo web desenvolvido para automatizar a extração de dados de documentos financeiros digitais, como comprovantes de pagamento, transferências Pix e extratos bancários nos formatos **PDF**, **JPEG** e **PNG**.

O sistema identifica automaticamente a instituição financeira, aplica técnicas de **OCR** e **pré-processamento de texto** para extrair campos relevantes (nome do recebedor, valor, data e ID da transação), e disponibiliza os dados estruturados para exportação em **CSV/Excel**.

---

## ✨ Funcionalidades

- Upload de documentos nos formatos PDF, JPG e PNG
- Detecção automática da instituição financeira
- Extração direta de texto em PDFs nativos (via `pdfplumber`)
- Fallback automático para OCR em documentos digitalizados (via `Tesseract`)
- Preview paginado do documento enviado
- Visualização dos dados extraídos em tempo real
- Exportação dos resultados em formato CSV
- Autenticação de usuários com senhas protegidas por hash
- Interface responsiva com modo claro/escuro

---

## 🏦 Instituições Suportadas

| Banco | Status |
|-------|--------|
| Nubank | ✅ Suportado |
| Banco Inter | ✅ Suportado |
| Caixa Econômica Federal | ✅ Suportado |
| Santander | ✅ Suportado |
| Santander Empresarial | ✅ Suportado |
| Itaú | ✅ Suportado |

---

## 🗂️ Estrutura do Projeto

```
TCC-Sistema-de-Extracao/
│
├── app.py              # Aplicação Flask — rotas, autenticação, exportação
├── main.py             # Processador central — PDF, imagem e roteamento por banco
├── database.py         # Conexão e criação de tabelas (PostgreSQL)
├── iniciar.py          # Script de inicialização
│
├── bancos/             # Parsers específicos por instituição financeira
│   ├── banco_inter.py
│   ├── banco_caixa.py
│   ├── banco_itau.py
│   ├── banco_nubank.py
│   ├── banco_santander.py
│   └── banco_santander_empresarial.py
│
├── utils/              # Utilitários de OCR e identificação de banco
│   ├── identificador.py
│   └── ocr.py
│
├── templates/          # Templates HTML (Jinja2)
├── static/             # Arquivos CSS e JavaScript
│
├── .env                # Variáveis de ambiente (não versionar em produção)
└── usuarios.db         # Banco de dados local SQLite (desenvolvimento)
```

---

## ⚙️ Tecnologias Utilizadas

**Back-end**
- Python 3.x
- Flask
- pdfplumber
- PyMuPDF (fitz)
- Tesseract OCR + pytesseract
- pdf2image + Poppler
- Pillow
- psycopg2 (PostgreSQL)
- Werkzeug (hash de senhas)

**Front-end**
- HTML5, CSS3, JavaScript
- Design responsivo com suporte a modo claro/escuro

**Banco de Dados**
- PostgreSQL (produção)
- SQLite (desenvolvimento local)

---

## 🚀 Como Executar Localmente

### Pré-requisitos

- Python 3.10+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) instalado e configurado no PATH
- [Poppler](https://poppler.freedesktop.org/) instalado
- PostgreSQL (opcional — pode usar SQLite para testes locais)

### Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/antoniomessias/TCC-Sistema-de-Extracao.git
cd TCC-Sistema-de-Extracao

# 2. Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows

# 3. Instale as dependências
pip install flask pdfplumber pymupdf pytesseract pdf2image pillow psycopg2-binary werkzeug pandas codetiming pdfplumber
```

### Configuração

No arquivo `main.py`, ajuste os caminhos do Tesseract e do Poppler conforme sua instalação:

```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_DIR = r"C:\poppler-25.07.0\Library\bin"
```

Configure o arquivo `.env` com a string de conexão ao banco de dados:

```
DATABASE_URL=postgresql://usuario:senha@localhost:5432/nome_do_banco
```

### Execução

```bash
python app.py
```

Acesse no navegador: `http://localhost:5000`

---

## 📊 Resultados Obtidos

Durante os testes realizados com uma base de **1.230 páginas** de documentos financeiros de múltiplas instituições:

| Métrica | Resultado |
|---|---|
| Páginas processadas | 1.230 |
| Extrações bem-sucedidas | 1.214 |
| Taxa de acurácia | ~98% |
| Tempo total de processamento | ~50 minutos |
| Tempo médio por página (PDF texto) | ~2,5 segundos |
| Tempo médio por página (OCR) | ~3,0 segundos |
| Ganho de eficiência vs. processo manual | 60x a 70x mais rápido |

---

## 🔒 Segurança

- Senhas armazenadas com hash seguro (Werkzeug)
- Queries parametrizadas para prevenção de SQL Injection
- Controle de sessão com limpeza total no logout
- Arquivos temporários removidos automaticamente ao encerrar a sessão
- Dados processados mantidos apenas na memória durante a sessão

---

## 🛣️ Trabalhos Futuros

- Suporte a mais instituições financeiras
- Integração de modelos NLP/LLM para extração semântica
- Aprendizado contínuo com feedback do usuário
- Migração para arquitetura de microserviços
- Integração com APIs bancárias para validação de transações

---

## 📚 Referências

- SMITH, R. An overview of the Tesseract OCR engine. IEEE, 2007.
- VASWANI, A. et al. Attention is all you need. NeurIPS, 2017.
- PRESSMAN, R.; MAXIM, B. Software Engineering: A Practitioner's Approach. McGraw-Hill, 2014.
- SCHWABER, K.; SUTHERLAND, J. The Scrum Guide. Scrum.org, 2017.

---

## 📝 Licença

Este projeto foi desenvolvido como Trabalho de Conclusão de Curso (TCC) no IFSP Campus Campinas em 2026. Uso acadêmico.

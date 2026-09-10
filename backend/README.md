# Backend e API do portal LABTEC.IN

Este diretório contém o backend Django que funciona como CMS institucional e API pública do portal LABTEC.IN. O LABTEC.IN é a unidade raiz e a LATEC é uma unidade filha atendida pelo mesmo backend.

A aplicação é testada diretamente pelo Django, sem precisar iniciar o frontend estático separado. O portal público é servido pelo próprio Django através de templates server-rendered, HTMX e Alpine.js. O frontend estático em `latec-app/` permanece como cliente separado: ele não acessa o banco nem replica regras de publicação. Ele consome os dados públicos de `/api/v1/` e usa os slugs e URLs devolvidos pela API.

## 1. Preparação e instalação

### Pré-requisitos

- Python 3 com suporte a ambientes virtuais;
- `pip`;
- SQLite, já suportado pelo Python, para o desenvolvimento local.

PostgreSQL é o banco previsto para homologação e produção, mas não é necessário para começar a integrar o frontend.

### Instalação

Na raiz do repositório:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/base.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_initial_data
# Apenas em desenvolvimento ou homologação:
python manage.py seed_edge_case_data --password senha-de-teste
python manage.py runserver
```

No Windows PowerShell, a ativação normalmente é:

```powershell
.venv\Scripts\Activate.ps1
```

**Sobre o ambiente virtual (`.venv`):** o `.venv/` é uma pasta que isola as dependências (bibliotecas) do projeto do Python que já existe no seu computador. É como se fosse uma "gaveta separada" só pra esse projeto. Sempre que for trabalhar aqui, ative o `.venv` primeiro — senão comandos como `python` e `pip` vão usar o Python global do seu PC, que pode não ter as libs do projeto. O `.venv/` **não deve ir pro git** (já tá no `.gitignore`); use `requirements/base.txt` pra instalar as dependências dentro dele.

### Inicializando tudo (um-passe)

Se quiser subir o ambiente do zero com segurança, execute essa sequência na pasta `backend/`:

```bash
python -m venv .venv          # Cria o ambiente virtual (uma vez)
source .venv/bin/activate      # Ativa no Linux/macOS  (ou .venv\Scripts\Activate.ps1 no Windows)
pip install -r requirements/base.txt   # Instala dependências
cp .env.example .env           # Copia config de ambiente
python manage.py migrate       # Cria/atualiza tabelas no banco
python manage.py seed_initial_data    # Popula dados iniciais
python manage.py seed_edge_case_data --password senha-de-teste   # (Opcional) dados de borda
python manage.py runserver    # Sobe o servidor
```

Pronto! Acesse `http://127.0.0.1:8000/` e a documentação da API em `http://127.0.0.1:8000/api/docs/`.

### O que cada comando faz

| Comando | O que faz |
|---|---|
| `cd backend` | Entra na pasta onde está o projeto Django |
| `python -m venv .venv` | Cria um **ambiente virtual** Python isolado |
| `source .venv/bin/activate` | **Ativa** o ambiente virtual (o prompt mostrará `(venv)`) |
| `pip install -r requirements/base.txt` | Instala todas as dependências do projeto |
| `cp .env.example .env` | Copia as variáveis de ambiente para configuração local |
| `python manage.py migrate` | Cria/atualiza as tabelas no banco (estrutura/schema) |
| `python manage.py seed_initial_data` | Inicializa uma base vazia com dados e mídia canônicos |
| `python manage.py seed_edge_case_data` | Popula dados de borda para testes |
| `python manage.py runserver` | Inicia o servidor de desenvolvimento local |

### `migrate` vs `seed`

- **`migrate`** → estrutura (schema). Cria tabelas, colunas, índices, chaves estrangeiras.
- **`seed`** → dados (conteúdo). Insere registros dentro das tabelas já criadas.

**Resumo:** `migrate` = cria as gavetas; `seed` = enche as gavetas com conteúdo.

### Fluxo de trabalho (do zero)

```bash
python manage.py migrate
python manage.py seed_initial_data
# Opcional, somente em desenvolvimento ou homologação:
python manage.py seed_edge_case_data --password senha-de-teste
python manage.py runserver
```

### Limpar o banco para testes limpos

Para **apagar todos os dados** e começar do zero:

**Opção 1 — `flush`** (limpa os dados, mantém a estrutura):
```bash
python manage.py flush --no-input
```

**Opção 2 — deletar o arquivo** (limpeza completa, recria tudo):
```bash
rm db.sqlite3
python manage.py migrate
```

Depois de limpar, repovoe:
```bash
python manage.py seed_initial_data
python manage.py seed_edge_case_data --password senha-de-teste
```

> **Nota:** `seed_initial_data` só pode ser executado em uma base vazia; após criar o LABTEC.IN, ele falha para proteger alterações feitas no Admin. `seed_edge_case_data` continua idempotente. `createsuperuser` cria um admin Django separado (sem vínculo institucional).

### Reset rápido local (desenvolvimento ou homologação)

Para reiniciar uma base de desenvolvimento ou homologação, sem preservar seu conteúdo:

1. **Pare o servidor** (Ctrl+C no terminal do `runserver`);
2. **Limpe o banco** (escolha uma opção):
   ```bash
   python manage.py flush --no-input   # rápido, mantém estrutura
   # ou
   rm db.sqlite3                          # completo, apaga tudo
   ```
3. **Recrie e repova:**
   ```bash
   python manage.py migrate
   python manage.py seed_initial_data
   python manage.py seed_edge_case_data --password senha-de-teste
   ```
4. **Reinicie:**
   ```bash
   python manage.py runserver
   ```

### Dados de borda

Para testar rascunhos, conteúdos arquivados, vínculos inativos e permissões:

```bash
python manage.py seed_edge_case_data --password senha-de-teste
```

Execute-o depois de `seed_initial_data`. A opção `--password` é opcional: sem ela, os usuários de teste não são criados; com ela, recebem a senha informada. Esses usuários não são superusuários.

### Primeiro deploy de produção

Em produção, use PostgreSQL e um `MEDIA_ROOT` vazio em volume persistente. Faça backup do banco e do volume de mídia no mesmo procedimento. Com as variáveis de produção configuradas, execute uma única vez:

```bash
python manage.py migrate
python manage.py seed_initial_data
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

O seed copia os ativos versionados em `backend/seed_assets/` para o volume de mídia e falha se algum arquivo obrigatório estiver ausente. Nos deploys seguintes, não execute o seed: aplique migrations, execute `collectstatic` e administre conteúdos, imagens e publicação pelo Django Admin.

| Usuário | Perfil |
|---|---|
| `edge-lab-coordinator` | Coordenação LABTEC.IN |
| `edge-unit-coordinator` | Coordenação LATEC |
| `edge-mentor` | Orientador da LATEC (eixo 1) |
| `edge-inactive-admin` | Usuário administrativo inativo |
| `edge-wrong-lab-coordinator` | Perfil LABTEC inválido |
| `edge-no-profile` | Usuário sem Profile |

A senha de todos é: `senha-de-teste`

### Testar em banco limpo (sem tocar o banco de desenvolvimento)

Use um SQLite temporário via variáveis de ambiente:

Linux/macOS:
```bash
DATABASE_URL=sqlite:////tmp/labtec-clean.sqlite3 \
MEDIA_ROOT=/tmp/labtec-clean-media \
python manage.py migrate
```

Windows PowerShell:
```powershell
$env:DATABASE_URL="sqlite:///C:/tmp/labtec-clean.sqlite3"
$env:MEDIA_ROOT="C:/tmp/labtec-clean-media"
python manage.py migrate
```

Depois, siga o mesmo fluxo: `seed_initial_data` → `seed_edge_case_data --password senha-de-teste` → `runserver`.

## 2. Iniciar o servidor

```bash
python manage.py runserver
```

Acesse: `http://127.0.0.1:8000/`

## 3. Testar as páginas públicas

Principais URLs:

```text
/
/unidades/latec/
/sobre/
/portfolio/
/portfolio/projetos/
/portfolio/projetos/startups/
/portfolio/projetos/farma-amazonia/
/portfolio/pesquisas/
/portfolio/tccs/
/portfolio/producao-cientifica/
/portfolio/transparencia/
/noticias/
/capacitacao/
/parceiros/
/contato/
/busca/
```

Teste também: `http://127.0.0.1:8000/portfolio/projetos/startups/`

Você deve visualizar: Farma Amazônia, Remédio Vivo, Amazon Green Line.

## 4. Testar autenticação e permissões

A tela de login está em: `http://127.0.0.1:8000/entrar/`

| Usuário | Perfil | Permissões |
|---|---|---|
| `edge-lab-coordinator` | Coordenação LABTEC.IN | Acessa tudo, publica e edita |
| `edge-unit-coordinator` | Coordenação LATEC | Cria/edita rascunhos, não publica |
| `edge-mentor` | Orientador da LATEC | Cria/edita rascunhos nos próprios eixos, não publica |
| `edge-no-profile` | Sem Profile | `is_staff=True`, mas não usa admin efetivamente |
| `edge-inactive-admin` | Inativo | Acesso recusado |

Senha de todos: `senha-de-teste`

Após login, o dashboard está em: `http://127.0.0.1:8000/admin/dashboard/`

## 5. Testar a busca global

```text
http://127.0.0.1:8000/busca/
```

Digite `Farma`. A busca usa HTMX e consulta `GET /api/v1/search/?q=Farma`.

Também via `curl`:
```bash
curl "http://127.0.0.1:8000/api/v1/search/?q=Farma"
curl "http://127.0.0.1:8000/api/v1/search/?q=Farma&type=project&unit=latec"
```

## 6. Testar o formulário de contato

```text
http://127.0.0.1:8000/contato/
```

O formulário envia para `POST /api/v1/contact/`. Após envio, aparece "Mensagem enviada com sucesso." Verifique no Admin em `/admin/partnerships/contactmessage/` (status inicial: `new`).

Via `curl`:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/contact/ \
  -d "contact_type=questions" -d "subject=Teste" \
  -d "name=Pessoa de Teste" -d "email=teste@example.com" \
  -d "message=Mensagem de teste"
```

## 7. Configurar o frontend e o CORS

O `.env.example` permite frontend em `http://localhost:5500` ou `http://127.0.0.1:5500`. Para outras origens:

```env
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Origem inclui protocolo, host e porta. Mantenha dois terminais: backend em `http://127.0.0.1:8000` e frontend na porta do seu framework.

URLs úteis:
- API: `http://127.0.0.1:8000/api/v1/`
- Docs: `http://127.0.0.1:8000/api/docs/`
- OpenAPI: `http://127.0.0.1:8000/api/schema/`
- Admin: `http://127.0.0.1:8000/admin/`
- Login: `http://127.0.0.1:8000/entrar/`

## 8. Testar a API pública

```bash
curl http://127.0.0.1:8000/api/v1/institutional-units/
curl http://127.0.0.1:8000/api/v1/projects/
curl http://127.0.0.1:8000/api/v1/posts/
curl http://127.0.0.1:8000/api/v1/courses/
```

## 9. Executar os testes automatizados

```bash
python manage.py check
python manage.py test
python manage.py makemigrations --check --dry-run
python manage.py spectacular --file /tmp/labtec-openapi.yaml --validate
git diff --check
```

## 10. Regras do frontend

### API pública
Catálogos são anônimos e somente leitura. A única escrita anônima é `POST /api/v1/contact/`. Conteúdos aparecem somente quando `editorial_status=published`.

### Paginação
Lista paginada com 20 itens por página:
```json
{"count": 42, "next": "...?page=2", "previous": null, "results": []}
```

### Slug
Monte links com o `slug` recebido da API. Não derive do título.

### Unidade institucional
Todo conteúdo tem uma unidade proprietária. `?unit=<slug>` retorna conteúdo próprio + filhas diretas aprovadas.

### Arquivos e mídia
Use diretamente as URLs retornadas pela API. Campos opcionais podem ser `null`, `""` ou listas vazias.

### Mapa de endpoints

| Tela | Endpoint | Observações |
| --- | --- | --- |
| Home | `GET /api/v1/site/home/` | Apenas LABTEC.IN |
| Unidades | `GET /api/v1/institutional-units/` | Lista todas |
| Pessoas | `GET /api/v1/people/` | Com memberships públicos |
| Eixos | `GET /api/v1/axes/` | Com mentorias |
| Projetos | `GET /api/v1/projects/` | Com equipe, resultados, links |
| Pesquisas | `GET /api/v1/research-projects/` | Com eixo e equipe |
| Trabalhos acadêmicos | `GET /api/v1/academic-works/` | Com pesquisa e contribuidores |
| Produções científicas | `GET /api/v1/scientific-outputs/` | Com autorias |
| Notícias | `GET /api/v1/posts/` | Sem categoria/tags/autores |
| Cursos | `GET /api/v1/courses/` | Com instrutores e materiais |
| Transparência | `GET /api/v1/transparency-documents/` | Detalhe por slug |
| Parceiros | `GET /api/v1/partners/` | Podem ter várias unidades |
| Métricas | `GET /api/v1/metrics/impact/` | Detalhe por `key` |
| Contato | `POST /api/v1/contact/` | Única escrita anônima |

### Filtros de catálogo

| Catálogo | Filtros |
| --- | --- |
| Projetos | `unit`, `axis`, `category`, `status`, `year`, `search` |
| Notícias | `unit`, `axis`, `year`, `search` |
| Cursos | `unit`, `axis`, `year`, `search` |
| Pesquisas | `unit`, `axis`, `project_status`, `year`, `search` |
| Trabalhos acadêmicos | `unit`, `work_type`, `year`, `search` |
| Produções científicas | `unit`, `axis`, `year`, `search` |
| Transparência | `unit`, `year`, `search` |

### Exemplos com `fetch`

```js
const API_URL = "http://127.0.0.1:8000/api/v1";

// Carregar lista paginada
async function listPosts(unit) {
  const response = await fetch(`${API_URL}/posts/?${new URLSearchParams({ unit })}`);
  if (!response.ok) throw new Error(`Falha: ${response.status}`);
  const page = await response.json();
  return page.results;
}

// Carregar detalhe por slug
async function getResearchProject(slug) {
  const response = await fetch(`${API_URL}/research-projects/${encodeURIComponent(slug)}/`);
  if (response.status === 404) return null;
  if (!response.ok) throw new Error(`Falha: ${response.status}`);
  return response.json();
}

// Enviar mensagem de contato
async function sendContact(form) {
  const response = await fetch(`${API_URL}/contact/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      contact_type: form.contactType, subject: form.subject,
      name: form.name, email: form.email,
      organization: form.organization || "", message: form.message,
    }),
  });
  const body = await response.json();
  if (response.status === 201) return body;
  if (response.status === 400) throw new Error(JSON.stringify(body));
  throw new Error(`Falha: ${response.status}`);
}
```

Datas são strings ISO (`2026-07-21` ou `2026-07-21T14:30:00-05:00`). Converta de fuso na camada de apresentação.

## 11. Diagnóstico rápido

- **Erro de CORS:** confira protocolo, host e porta em `CORS_ALLOWED_ORIGINS` e reinicie o Django.
- **Lista vazia:** confirme se o seed foi executado e se o conteúdo está publicado.
- **`404` em detalhe:** use o slug devolvido pela lista; não derive do título.
- **Imagem/PDF não abre:** use a URL da API e confirme `DEBUG=True`.
- **Mudou o `.env`:** reinicie o servidor.
- **Erro de migration:** restaure o backup antes de corrigir dados manualmente.

# Backend e API do portal LABTEC.IN

Este diretório contém o backend Django que funciona como CMS institucional e API pública do portal LABTEC.IN. O LABTEC.IN é a unidade raiz e a LATEC é uma unidade filha atendida pelo mesmo backend.

A aplicação agora é testada diretamente pelo Django, sem precisar iniciar o frontend estático separado. O portal público é servido pelo próprio Django através de templates server-rendered, HTMX e Alpine.js. O frontend estático em `latec-app/` permanece como cliente separado: ele não acessa o banco nem replica regras de publicação. Ele consome os dados públicos de `/api/v1/` e usa os slugs e URLs devolvidos pela API.

## 1. Preparar o ambiente

Na raiz do projeto:

```bash
cd backend
```

Ative o ambiente virtual.

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Se ainda não instalou as dependências:

```bash
pip install -r requirements/base.txt
```

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
python manage.py seed_edge_case_data --password senha-de-teste
python manage.py runserver
```

No Windows PowerShell, a ativação normalmente é:

```powershell
.venv\Scripts\Activate.ps1
```

## 2. Criar o banco e os dados iniciais

Execute:

```bash
python manage.py migrate
python manage.py seed_initial_data
```

O seed cria:

- LABTEC.IN como unidade raiz;
- LATEC como unidade filha;
- pessoas e vínculos institucionais;
- projetos;
- startups;
- pesquisas;
- notícias;
- cursos;
- métricas;
- configurações do site;
- banners e seções institucionais.

O comando é idempotente, portanto pode ser executado novamente:

```bash
python manage.py seed_initial_data
```

Ele não cria usuários.

### O que cada comando adiciona

`python manage.py migrate` aplica as migrations do Django e cria ou atualiza a estrutura das tabelas. Ele não popula o conteúdo institucional e não cria usuários administrativos.

`python manage.py seed_initial_data` cria os dados canônicos para desenvolvimento e homologação. Entre eles estão:

- LABTEC.IN como unidade raiz e LATEC como unidade filha;
- 36 pessoas, 43 vínculos institucionais e três perfis de startup;
- eixos, mentorias, projetos, pesquisas, notícias, cursos e materiais;
- métricas de impacto;
- configurações do site, banner e seções institucionais.

Esse comando é idempotente: pode ser executado novamente sem duplicar os registros. Ele não cria usuários, senhas ou credenciais administrativas.

`python manage.py createsuperuser` cria um usuário administrativo do Django com acesso ao `/admin/`. O comando solicita nome de usuário, e-mail e senha. Ele não cria uma `Person` nem um `Profile` institucional automaticamente.

Esta versão suporta inicialização limpa: em desenvolvimento, teste e homologação, descarte a base configurada e o `MEDIA_ROOT` de teste antes de executar `migrate` e `seed_initial_data`. Não há caminho de atualização *in-place* para uma base populada anterior ao corte institucional; a migration falha intencionalmente ao encontrar conteúdo legado sem unidade.

## 3. Criar dados de borda

Para testar rascunhos, conteúdos arquivados, vínculos inativos e permissões:

```bash
python manage.py seed_edge_case_data --password senha-de-teste
```

Esse comando adiciona dados artificiais para testar situações de borda, como:

- unidades descendentes e uma unidade raiz independente;
- pessoas sem vínculo, com múltiplos vínculos, vínculos inativos ou futuros;
- conteúdos publicados, em rascunho, em revisão e arquivados;
- parceiros, mensagens de contato, links sociais e snapshots de métricas;
- perfis administrativos com escopos institucionais diferentes.

Execute-o depois de `seed_initial_data`. Ele também é idempotente. A opção `--password` é opcional: sem ela, os dados administrativos não são criados; com ela, os usuários de teste recebem a senha informada. Esses usuários não são superusuários.

Esse comando cria usuários de teste:

| Usuário | Perfil |
|---|---|
| `edge-lab-coordinator` | Coordenação LABTEC.IN |
| `edge-unit-coordinator` | Coordenação LATEC |
| `edge-mentor` | Mentor |
| `edge-inactive-admin` | Usuário administrativo inativo |
| `edge-wrong-lab-coordinator` | Perfil LABTEC inválido |
| `edge-no-profile` | Usuário sem Profile |

A senha de todos é:

```text
senha-de-teste
```

Execute o comando novamente para confirmar a idempotência:

```bash
python manage.py seed_edge_case_data --password senha-de-teste
```

## 4. Iniciar o servidor

```bash
python manage.py runserver
```

Acesse:

```text
http://127.0.0.1:8000/
```

O portal público agora é servido pelo Django.

## 5. Testar as páginas públicas

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

Teste também diretamente no navegador:

```text
http://127.0.0.1:8000/portfolio/projetos/startups/
```

Você deve visualizar:

- Farma Amazônia;
- Remédio Vivo;
- Amazon Green Line.

## 6. Testar autenticação administrativa

A tela de login está em:

```text
http://127.0.0.1:8000/entrar/
```

Teste com:

```text
Usuário: edge-lab-coordinator
Senha: senha-de-teste
```

Após o login, você será direcionado para:

```text
/admin/dashboard/
```

O dashboard permite:

- visualizar contagens por status editorial;
- filtrar por unidade;
- acessar o Django Admin;
- retornar ao portal público;
- encerrar a sessão.

Também é possível acessar diretamente:

```text
http://127.0.0.1:8000/admin/
```

No Django Admin, teste:

- projetos;
- perfis administrativos;
- pessoas;
- unidades;
- notícias;
- pesquisas;
- startups;
- mensagens de contato.

## 7. Testar permissões

### Coordenação LABTEC.IN

Login:

```text
edge-lab-coordinator
```

Deve conseguir:

- acessar o dashboard;
- acessar conteúdos do LABTEC.IN e unidades descendentes;
- publicar conteúdos;
- editar conteúdos publicados;
- gerenciar memberships dentro do escopo permitido.

### Coordenação LATEC

Login:

```text
edge-unit-coordinator
```

Deve conseguir:

- acessar o Admin;
- trabalhar somente com conteúdos da LATEC;
- criar e editar rascunhos;
- não publicar conteúdos finais;
- não alterar conteúdos já publicados.

### Mentor

Login:

```text
edge-mentor
```

Deve ter escopo limitado aos eixos e conteúdos permitidos para sua atuação.

### Usuário sem Profile

Login:

```text
edge-no-profile
```

Esse usuário possui `is_staff=True`, mas não deve conseguir utilizar a área administrativa efetivamente.

### Usuário inativo

Login:

```text
edge-inactive-admin
```

O acesso deve ser recusado.

## 8. Testar a busca global

Acesse:

```text
http://127.0.0.1:8000/busca/
```

Digite, por exemplo:

```text
Farma
```

A busca usa HTMX e consulta:

```text
GET /api/v1/search/?q=Farma
```

Também é possível testar diretamente:

```bash
curl "http://127.0.0.1:8000/api/v1/search/?q=Farma"
```

Filtrando por tipo:

```bash
curl "http://127.0.0.1:8000/api/v1/search/?q=Farma&type=project"
```

Filtrando por unidade:

```bash
curl "http://127.0.0.1:8000/api/v1/search/?q=Farma&type=project&unit=latec"
```

A resposta deve ter esta estrutura:

```json
{
  "count": 1,
  "results": [
    {
      "type": "project",
      "title": "Farma Amazônia",
      "slug": "farma-amazonia",
      "summary": "...",
      "unit": {
        "name": "LATEC",
        "slug": "latec"
      },
      "url": "/portfolio/projetos/farma-amazonia/"
    }
  ]
}
```

Crie ou mantenha um projeto em rascunho e confirme que ele não aparece na busca pública.

## 9. Testar o formulário de contato

Acesse:

```text
http://127.0.0.1:8000/contato/
```

Preencha:

- nome;
- e-mail;
- assunto;
- tipo de contato;
- mensagem.

O formulário envia para:

```text
POST /api/v1/contact/
```

Após o envio, deve aparecer:

```text
Mensagem enviada com sucesso.
```

A mensagem pode ser conferida no Admin:

```text
/admin/partnerships/contactmessage/
```

O status inicial deve ser:

```text
new
```

Para testar erro, envie campos vazios ou um e-mail inválido. O formulário deve mostrar os erros sem recarregar a página.

Também é possível testar via `curl`:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/contact/ \
  -d "contact_type=questions" \
  -d "subject=Teste" \
  -d "name=Pessoa de Teste" \
  -d "email=teste@example.com" \
  -d "message=Mensagem de teste"
```

## 10. Configurar o frontend e o CORS

O arquivo `.env.example` já permite, em desenvolvimento, um frontend servido em `http://localhost:5500` ou `http://127.0.0.1:5500`. Se o frontend usar outra origem, inclua a origem completa em `CORS_ALLOWED_ORIGINS`, separando os valores por vírgula e sem espaços:

```env
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Origem inclui protocolo, host e porta. Portanto, `http://localhost:5173` e `http://127.0.0.1:5173` são origens diferentes.

Uma forma simples de trabalhar é manter dois terminais:

```txt
Terminal 1: backend Django em http://127.0.0.1:8000
Terminal 2: frontend em http://localhost:5500 (ou a porta da ferramenta usada)
```

URLs úteis:

- API: `http://127.0.0.1:8000/api/v1/`
- documentação interativa: `http://127.0.0.1:8000/api/docs/`
- schema OpenAPI: `http://127.0.0.1:8000/api/schema/`
- Django Admin: `http://127.0.0.1:8000/admin/`
- mídia em desenvolvimento: `http://127.0.0.1:8000/media/...`
- portal server-rendered: `http://127.0.0.1:8000/`
- login administrativo: `http://127.0.0.1:8000/entrar/`
- dashboard administrativo: `http://127.0.0.1:8000/admin/dashboard/`

As páginas públicas usam templates Django, HTMX para atualizações parciais e Alpine.js para estado local. O Django Admin continua sendo o CRUD editorial principal.

## 11. Testar a API pública existente

Documentação interativa:

```text
http://127.0.0.1:8000/api/docs/
```

Schema OpenAPI:

```text
http://127.0.0.1:8000/api/schema/
```

Exemplos:

```bash
curl http://127.0.0.1:8000/api/v1/institutional-units/
curl http://127.0.0.1:8000/api/v1/projects/
curl http://127.0.0.1:8000/api/v1/projects/farma-amazonia/
curl http://127.0.0.1:8000/api/v1/research-projects/
curl http://127.0.0.1:8000/api/v1/posts/
curl http://127.0.0.1:8000/api/v1/courses/
```

Projetos de startup devem retornar o campo:

```json
"startup_profile": {
  "focus_area": "...",
  "species_or_subject": "...",
  "institution": "UFAC/LABTEC.IN"
}
```

## 12. Executar os testes automatizados

Verificação do Django:

```bash
python manage.py check
```

Todos os testes:

```bash
python manage.py test
```

Verificar migrations pendentes:

```bash
python manage.py makemigrations --check --dry-run
```

Validar o schema OpenAPI:

```bash
python manage.py spectacular \
  --file /tmp/labtec-openapi.yaml \
  --validate
```

Verificar problemas de whitespace no diff:

```bash
git diff --check
```

## 13. Testar em banco limpo

Para não apagar seu banco de desenvolvimento atual, use um SQLite temporário:

Linux/macOS:

```bash
cd backend

DATABASE_URL=sqlite:////tmp/labtec-clean.sqlite3 \
MEDIA_ROOT=/tmp/labtec-clean-media \
python manage.py migrate
```

Depois:

```bash
DATABASE_URL=sqlite:////tmp/labtec-clean.sqlite3 \
MEDIA_ROOT=/tmp/labtec-clean-media \
python manage.py seed_initial_data
```

Execute novamente:

```bash
DATABASE_URL=sqlite:////tmp/labtec-clean.sqlite3 \
MEDIA_ROOT=/tmp/labtec-clean-media \
python manage.py seed_initial_data
```

E execute os dados de borda duas vezes:

```bash
DATABASE_URL=sqlite:////tmp/labtec-clean.sqlite3 \
MEDIA_ROOT=/tmp/labtec-clean-media \
python manage.py seed_edge_case_data --password senha-de-teste

DATABASE_URL=sqlite:////tmp/labtec-clean.sqlite3 \
MEDIA_ROOT=/tmp/labtec-clean-media \
python manage.py seed_edge_case_data --password senha-de-teste
```

Para iniciar o servidor usando esse banco temporário:

```bash
DATABASE_URL=sqlite:////tmp/labtec-clean.sqlite3 \
MEDIA_ROOT=/tmp/labtec-clean-media \
python manage.py runserver
```

No Windows PowerShell, configure as variáveis antes:

```powershell
$env:DATABASE_URL="sqlite:///C:/tmp/labtec-clean.sqlite3"
$env:MEDIA_ROOT="C:/tmp/labtec-clean-media"

python manage.py migrate
python manage.py seed_initial_data
python manage.py seed_edge_case_data --password senha-de-teste
python manage.py runserver
```

O fluxo mínimo recomendado é:

```bash
python manage.py migrate
python manage.py seed_initial_data
python manage.py seed_edge_case_data --password senha-de-teste
python manage.py runserver
```

Depois teste:

1. `/`;
2. `/portfolio/projetos/startups/`;
3. `/busca/`;
4. `/contato/`;
5. `/entrar/`;
6. `/admin/dashboard/`;
7. `/admin/`;
8. `python manage.py test`.

## 14. Regras que o frontend precisa conhecer

### API pública

Os catálogos são anônimos e somente leitura. O frontend não precisa enviar token para fazer `GET`. A exceção de escrita pública é `POST /api/v1/contact/`.

A busca global está em `GET /api/v1/search/?q=termo&type=&unit=`. O formulário em `/busca/` usa HTMX e a resposta da API contém somente registros públicos. O formulário em `/contato/` usa o endpoint de contato; com `HX-Request: true`, ele recebe um fragmento HTML de sucesso ou validação.

Conteúdos editoriais aparecem somente quando `editorial_status=published`. Rascunhos, conteúdos em revisão e arquivados não são devolvidos, e os campos administrativos de workflow não fazem parte dos payloads públicos.

### Paginação

As rotas de lista usam paginação de 20 itens por padrão:

```json
{
  "count": 42,
  "next": "http://127.0.0.1:8000/api/v1/posts/?page=2",
  "previous": null,
  "results": []
}
```

O frontend deve renderizar os itens de `results` e usar `next` e `previous` para navegar. A Home é um objeto agregado e não usa esse envelope.

### Slug

Slug é o identificador legível usado na URL. Por exemplo, o título "Pesquisa de Bioativos da Amazônia" usa o slug `pesquisa-de-bioativos-da-amazonia`:

```txt
GET /api/v1/research-projects/pesquisa-de-bioativos-da-amazonia/
```

O frontend deve montar links com o `slug` recebido na resposta, nunca recalculá-lo a partir do título nem manter listas fixas de slugs.

Dois slugs de notícias foram corrigidos de forma incompatível e não possuem redirecionamento:

- `coordenadora-da-latec-e-premiada-por-inovacao-tecnologica` substitui a versão com `latecin`;
- `latec-participa-do-congresso-nacional-de-inovacao` substitui a versão com `latecin`.

As URLs antigas retornam `404`.

### Unidade institucional

Toda unidade cadastrada é pública. Não existem flags para ocultar ou desativar uma `InstitutionalUnit`. A representação resumida usada dentro dos conteúdos é:

```json
{
  "name": "LABTEC.IN",
  "acronym": "LABTEC.IN",
  "slug": "labtec-in",
  "unit_type": "laboratory"
}
```

Cada conteúdo possui uma única unidade proprietária. Nos sete catálogos editoriais que participam do ecossistema — projetos, notícias, cursos, pesquisas, trabalhos acadêmicos, produções científicas e transparência — `?unit=<slug>` retorna:

1. conteúdo próprio da unidade consultada;
2. conteúdo de filhas diretas que tenha sido aprovado para integrar o ecossistema da mãe.

Exemplo:

```txt
GET /api/v1/posts/?unit=latec
GET /api/v1/posts/?unit=labtec-in
```

Uma notícia pertencente à LATEC pode aparecer no segundo resultado, mas continuará serializando `unit.slug` como `latec`. A agregação alcança somente filhas diretas, não netas. Sem `?unit`, a API retorna o conteúdo publicado de todas as unidades.

A Home é deliberadamente diferente: `/api/v1/site/home/` traz somente configurações, banners, seções e links diretamente pertencentes ao LABTEC.IN.

### Arquivos e imagens

Use diretamente o valor de `file`, `cover_image`, `photo`, `logo` ou outro campo de mídia retornado pela API. Não concatene `/media/` manualmente. Campos opcionais podem ser `null`, `""` ou listas vazias; o frontend deve tratar esses casos sem quebrar a página.

Um material de curso não possui privacidade própria nem endpoint separado. Todos os itens de `materials` de um curso publicado são públicos e aparecem ordenados por `display_order`. O acesso ao material segue a publicação do curso.

## 15. Mapa de endpoints para as telas

| Tela ou dado | Método e endpoint | Observações |
| --- | --- | --- |
| Home | `GET /api/v1/site/home/` | Objeto com `settings`, `heroes`, `sections` e `social_links`; somente LABTEC.IN. |
| Configuração do site | `GET /api/v1/site/settings/` | Lista paginada; normalmente a Home já fornece a configuração necessária. |
| Unidades | `GET /api/v1/institutional-units/` | Lista todas as unidades; detalhe por slug. |
| Pessoas | `GET /api/v1/people/` | Inclui memberships públicos válidos; detalhe por slug. |
| Eixos | `GET /api/v1/axes/` | Inclui mentorias; detalhe por slug. |
| Categorias de portfólio | `GET /api/v1/projects/categories/` | Somente classificações práticas; não há categorias de pesquisa. |
| Projetos de portfólio | `GET /api/v1/projects/` | Detalhe por slug; inclui equipe, resultados e links. |
| Pesquisas | `GET /api/v1/research-projects/` | Detalhe por slug; inclui eixo e equipe. |
| Trabalhos acadêmicos | `GET /api/v1/academic-works/` | Detalhe por slug; inclui pesquisa e contribuidores. |
| Produções científicas | `GET /api/v1/scientific-outputs/` | Detalhe por slug; inclui relações e autorias. |
| Notícias | `GET /api/v1/posts/` | Detalhe por slug; não possui categoria, tags ou autores. |
| Cursos | `GET /api/v1/courses/` | Detalhe por slug; inclui instrutores e todos os materiais. |
| Transparência | `GET /api/v1/transparency-documents/` | Detalhe por slug. |
| Parceiros | `GET /api/v1/partners/` | Um parceiro pode estar ligado a várias unidades. |
| Métricas | `GET /api/v1/metrics/impact/` | Detalhe por `key`; não há endpoint público de snapshots. |
| Contato | `POST /api/v1/contact/` | Única escrita anônima da API. |

Não existem endpoints públicos de eventos, trilhas de aprendizagem, tags ou categorias de notícias, memberships isolados, snapshots de métricas ou MediaHub.

### Filtros de catálogo

| Catálogo | Filtros suportados |
| --- | --- |
| Projetos | `unit`, `axis`, `category`, `status`, `year`, `search` |
| Notícias | `unit`, `axis`, `year`, `search` |
| Cursos | `unit`, `axis`, `year`, `search` |
| Pesquisas | `unit`, `axis`, `project_status`, `year`, `search` |
| Trabalhos acadêmicos | `unit`, `work_type`, `year`, `search` |
| Produções científicas | `unit`, `axis`, `year`, `search` |
| Transparência | `unit`, `year`, `search` |

Os filtros podem ser combinados:

```txt
GET /api/v1/research-projects/?unit=latec&project_status=in_progress&search=bioativo
GET /api/v1/academic-works/?work_type=tcc&year=2026
```

Consulte `/api/docs/` para conferir enums e o contrato completo gerado pelo backend.

## 16. Exemplos com `fetch`

### Carregar uma lista paginada

```js
const API_URL = "http://127.0.0.1:8000/api/v1";

async function listPosts(unit) {
  const query = new URLSearchParams({ unit });
  const response = await fetch(`${API_URL}/posts/?${query}`);

  if (!response.ok) {
    throw new Error(`Falha ao carregar notícias: ${response.status}`);
  }

  const page = await response.json();
  return page.results;
}
```

### Carregar um detalhe por slug

```js
async function getResearchProject(slug) {
  const response = await fetch(
    `${API_URL}/research-projects/${encodeURIComponent(slug)}/`,
  );

  if (response.status === 404) return null;
  if (!response.ok) {
    throw new Error(`Falha ao carregar pesquisa: ${response.status}`);
  }

  return response.json();
}
```

### Enviar uma mensagem de contato

```js
async function sendContact(form) {
  const response = await fetch(`${API_URL}/contact/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      contact_type: form.contactType,
      subject: form.subject,
      name: form.name,
      email: form.email,
      organization: form.organization || "",
      message: form.message,
    }),
  });

  const body = await response.json();
  if (response.status === 201) return body;
  if (response.status === 400) {
    throw new Error(JSON.stringify(body));
  }
  throw new Error(`Falha ao enviar mensagem: ${response.status}`);
}
```

Datas são strings ISO, como `2026-07-21` ou `2026-07-21T14:30:00-05:00`. Faça a conversão de fuso somente na camada de apresentação.

## 17. Diagnóstico rápido

- **Erro de CORS:** confira protocolo, host e porta exatos em `CORS_ALLOWED_ORIGINS` e reinicie o Django.
- **Lista vazia:** confirme se o seed foi executado e se o conteúdo está publicado.
- **`404` em detalhe:** confira o slug devolvido pela lista; não derive o slug do título.
- **Imagem ou PDF não abre:** use a URL devolvida pela API e confirme que o servidor está com `DEBUG=True` no ambiente local.
- **Mudou o `.env`:** reinicie o servidor para recarregar a configuração.
- **Erro de migration:** restaure o backup antes de tentar corrigir dados manualmente.

O frontend deve tratar o OpenAPI como referência de contrato e este README como guia de integração e execução local.

# Backend e API do portal LABTEC.IN

Este diretório contém o backend Django que funciona como CMS institucional e API pública do portal LABTEC.IN. O LABTEC.IN é a unidade raiz e a LATEC é uma unidade filha atendida pelo mesmo backend.

O frontend é um cliente separado: ele não acessa o banco nem replica regras de publicação. Ele consome os dados públicos de `/api/v1/` e usa os slugs e URLs devolvidos pela API.

## 1. Preparar o ambiente local

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

### O que cada comando adiciona

`python manage.py migrate` aplica as migrations do Django e cria ou atualiza a estrutura das tabelas. Ele não popula o conteúdo institucional e não cria usuários administrativos.

`python manage.py seed_initial_data` cria os dados canônicos para desenvolvimento e homologação. Entre eles estão:

- LABTEC.IN como unidade raiz e LATEC como unidade filha;
- 33 pessoas e 43 vínculos institucionais;
- eixos, mentorias, projetos, pesquisa, notícias, cursos e materiais;
- métricas de impacto;
- configurações do site, banner e seções institucionais.

Esse comando é idempotente: pode ser executado novamente sem duplicar os registros. Ele não cria usuários, senhas ou credenciais administrativas.

`python manage.py seed_edge_case_data --password senha-de-teste` adiciona dados artificiais para testar situações de borda, como:

- unidades descendentes e uma unidade raiz independente;
- pessoas sem vínculo, com múltiplos vínculos, vínculos inativos ou futuros;
- conteúdos publicados, em rascunho, em revisão e arquivados;
- parceiros, mensagens de contato, links sociais e snapshots de métricas;
- perfis administrativos com escopos institucionais diferentes.

Execute-o depois de `seed_initial_data`. Ele também é idempotente. A opção `--password` é opcional: sem ela, os dados administrativos não são criados; com ela, os usuários de teste recebem a senha informada. Esses usuários não são superusuários.

`python manage.py createsuperuser` cria um usuário administrativo do Django com acesso ao `/admin/`. O comando solicita nome de usuário, e-mail e senha. Ele não cria uma `Person` nem um `Profile` institucional automaticamente.

No Windows PowerShell, a ativação normalmente é:

```powershell
.venv\Scripts\Activate.ps1
```

O backend ficará disponível em `http://127.0.0.1:8000`. Mantenha esse terminal aberto enquanto desenvolver o frontend.

Esta versão suporta inicialização limpa: em desenvolvimento, teste e homologação, descarte a base configurada e o `MEDIA_ROOT` de teste antes de executar `migrate` e `seed_initial_data`. Não há caminho de atualização *in-place* para uma base populada anterior ao corte institucional; a migration falha intencionalmente ao encontrar conteúdo legado sem unidade.

## 2. Configurar o frontend e o CORS

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

Receber `404` em `http://127.0.0.1:8000/` é normal: não existe página pública na raiz do backend. Use `/api/v1/` ou `/api/docs/`.

## 3. Regras que o frontend precisa conhecer

### API pública

Os catálogos são anônimos e somente leitura. O frontend não precisa enviar token para fazer `GET`. A exceção de escrita pública é `POST /api/v1/contact/`.

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

Slug é o identificador legível usado na URL. Por exemplo, o título “Pesquisa de Bioativos da Amazônia” usa o slug `pesquisa-de-bioativos-da-amazonia`:

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

## 4. Mapa de endpoints para as telas

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

## 5. Exemplos com `fetch`

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

## 6. Diagnóstico rápido

- **Erro de CORS:** confira protocolo, host e porta exatos em `CORS_ALLOWED_ORIGINS` e reinicie o Django.
- **Lista vazia:** confirme se o seed foi executado e se o conteúdo está publicado.
- **`404` em detalhe:** confira o slug devolvido pela lista; não derive o slug do título.
- **Imagem ou PDF não abre:** use a URL devolvida pela API e confirme que o servidor está com `DEBUG=True` no ambiente local.
- **Mudou o `.env`:** reinicie o servidor para recarregar a configuração.
- **Erro de migration:** restaure o backup antes de tentar corrigir dados manualmente.

## 7. Validação do backend

```bash
python manage.py check
python manage.py test
python manage.py makemigrations --check --dry-run
python manage.py spectacular --file /tmp/latec-openapi.yaml --validate
```

O frontend deve tratar o OpenAPI como referência de contrato e este README como guia de integração e execução local.

# API pública do portal LABTEC.IN

O backend expõe recursos anônimos e predominantemente somente leitura em `/api/v1/`, além do envio público de mensagens de contato. Conteúdos institucionais retornam uma unidade resumida:

```json
{
  "name": "LABTEC.IN",
  "acronym": "LABTEC.IN",
  "slug": "labtec-in",
  "unit_type": "laboratory"
}
```

A API é consumida pelo portal público server-rendered (via HTMX para requisições parciais) e por clientes externos. O portal também consulta o ORM diretamente através das web views em `apps/core/web_views.py`, sem passar pela API.

## Endpoints principais

```txt
GET /api/v1/site/home/
GET /api/v1/institutional-units/
GET /api/v1/institutional-units/{slug}/
GET /api/v1/people/
GET /api/v1/axes/
GET /api/v1/projects/categories/
GET /api/v1/projects/
GET /api/v1/projects/{slug}/
GET /api/v1/research-projects/
GET /api/v1/research-projects/{slug}/
GET /api/v1/academic-works/
GET /api/v1/academic-works/{slug}/
GET /api/v1/scientific-outputs/
GET /api/v1/scientific-outputs/{slug}/
GET /api/v1/posts/
GET /api/v1/posts/{slug}/
GET /api/v1/courses/
GET /api/v1/courses/{slug}/
GET /api/v1/transparency-documents/
GET /api/v1/partners/
GET /api/v1/metrics/impact/
POST /api/v1/contact/
GET /api/v1/search/?q=termo&type=&unit=
```

Não existem endpoints de tags de notícia, eventos, trilhas, MediaHub, memberships ou snapshots de métricas.

`institutional-units` lista todas as unidades cadastradas. Unidades são sempre públicas e o payload não possui `is_active` ou `is_public`; a unidade pai é resumida sempre que existir.

Projetos classificados como `startup` podem conter `startup_profile` com `focus_area`, `species_or_subject` e `institution`. Startups continuam sendo projetos; não existe endpoint independente. A busca global retorna `{count, results}` com `type`, `title`, `slug`, `summary`, `unit` e `url`, somente para registros públicos.

As respostas de `posts` incluem `cover_image`, `body_image` opcional e `links`, cada link com `label`, `url` e `display_order`.

## Publicação

Projetos, pesquisas, trabalhos, produções, notícias, cursos e documentos de transparência aparecem publicamente somente quando `editorial_status=published`. `published_at` registra o momento editorial, mas não é um segundo interruptor.

Banners e seções institucionais continuam usando a flag simples `is_published`, pois não participam do workflow editorial completo.

## Filtro por unidade e ecossistema

Os endpoints de conteúdo aceitam `?unit=<slug>`:

```txt
GET /api/v1/projects/?unit=latec
GET /api/v1/posts/?unit=labtec-in
GET /api/v1/research-projects/?unit=latec
```

O resultado contém:

1. registros cuja unidade proprietária é a unidade consultada;
2. registros de filhas diretas com `include_in_parent_ecosystem=True`.

A agregação não percorre netos, não altera a unidade serializada e não duplica propriedade. Sem `?unit`, a lista inclui conteúdo publicado de todas as unidades.

A regra de ecossistema vale para projetos, notícias, cursos, pesquisas, trabalhos acadêmicos, produções científicas e documentos de transparência. Parceiros são filtrados por sua relação M2M explícita; métricas e demais recursos usam somente propriedade direta.

## Filtros

| Endpoint | Filtros específicos |
| --- | --- |
| `projects` | `unit`, `axis`, `category`, `status`, `year`, `search` |
| `posts` | `unit`, `axis`, `year`, `search` |
| `courses` | `unit`, `axis`, `year`, `search` |
| `research-projects` | `unit`, `axis`, `project_status`, `year`, `search` |
| `academic-works` | `unit`, `work_type`, `year`, `search` |
| `scientific-outputs` | `unit`, `axis`, `year`, `search` |
| `transparency-documents` | `unit`, `year`, `search` |

Não existe filtro `featured`.

## Contratos resumidos

- Pessoas expõem memberships públicos ativos no formato `[{unit, role}]`; não existe papel público global.
- Notícias expõem unidade, eixo, título, slug, resumo, conteúdo, capa e data de publicação; não expõem categoria, tags, autores nem controles administrativos.
- Cursos expõem instrutores e todos os materiais ordenados. Material não possui privacidade própria e herda a publicação do curso.
- Pesquisas expõem metadados, arquivo/URL, eixo e equipe ordenada.
- Trabalhos expõem metadados bibliográficos, arquivo/URL, pesquisa resumida e contribuidores.
- Produções expõem metadados bibliográficos, arquivo/URL, relações resumidas e autoria interna ordenada.
- `include_in_parent_ecosystem` é administrativo e não integra os payloads públicos.

Representações aninhadas de pessoas são resumidas para evitar ciclos e consultas desnecessárias.

## Slugs corrigidos

O frontend deve usar o `slug` devolvido pela API. O corte final substituiu, sem aliases ou redirecionamentos:

- `coordenadora-do-latecin-e-premiada-por-inovacao-tecnologica` por `coordenadora-da-latec-e-premiada-por-inovacao-tecnologica`;
- `latecin-participa-do-congresso-nacional-de-inovacao` por `latec-participa-do-congresso-nacional-de-inovacao`.

As duas URLs antigas retornam `404`.

## Home

`/api/v1/site/home/` retorna somente configurações, banners, seções e links sociais vinculados diretamente a `labtec-in`. O opt-in de ecossistema não amplia esse payload. Pesquisas, projetos, notícias e cursos continuam disponíveis em seus endpoints próprios. O portal público server-rendered também consulta o ORM diretamente em `web_views.home` para compor a página inicial com dados do ecossistema.

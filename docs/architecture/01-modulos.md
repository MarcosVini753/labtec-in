# Módulos do backend do portal LABTEC.IN

O backend é dividido em apps Django por domínio. `institutional` centraliza a organização e `research` separa pesquisas e trabalhos acadêmicos do portfólio.

## Apps ativos

| App | Responsabilidade |
| --- | --- |
| `institutional` | Unidades, hierarquia e memberships. |
| `accounts` | Perfis administrativos e escopo autorizado por unidade. |
| `core` | Configurações, banners, seções institucionais, links sociais e web views do portal público. |
| `people` | Cadastro da pessoa física, independente de autenticação. |
| `axes` | Sete eixos da LATEC e mentorias. |
| `research` | Pesquisas formais, TCCs e outros trabalhos acadêmicos. |
| `portfolio` | Projetos práticos, extensão, produtos, serviços e soluções. |
| `scientific` | Produções científicas, autorias e relações com pesquisas e trabalhos. |
| `news` | Notícias institucionais, sem taxonomias ou autores próprios. |
| `learning` | Cursos e seus materiais. |
| `transparency` | Documentos de transparência. |
| `partnerships` | Parceiros por unidade e mensagens de contato. |
| `metrics` | Métricas e históricos de valores por unidade. |
| `common` | Modelos-base, status editorial, busca global, middleware e utilidades compartilhadas. |

Não existe app ou catálogo central de mídia. Cada arquivo pertence diretamente ao modelo de domínio que o publica.

## Relações centrais

- `institutional` fornece unidade, hierarquia e memberships.
- `people` se relaciona com memberships, mentorias, equipes, contribuições e autorias.
- `axes` classifica opcionalmente conteúdo ligado à atuação da LATEC.
- `research` pode originar registros em `scientific`.
- `accounts` protege o Django Admin por unidade, descendência e eixo.
- `metrics` registra valores informados; não calcula agregações automaticamente.

O [mapa de módulos](diagrams/module-map.md) representa as dependências persistidas.

## Delimitação entre domínios

- Pesquisa formal: `research.ResearchProject`.
- TCC ou outro trabalho acadêmico: `research.AcademicWork`.
- Resultado científico publicado: `scientific.ScientificOutput`.
- Iniciativa prática, produto ou solução: `portfolio.Project`.
- Capacitação: `learning.Course` e materiais associados.

Todos os materiais associados a um curso publicado são públicos. `CourseMaterial` não possui workflow ou flag de visibilidade independente.

Não existem mais models de trilha, evento, categoria ou tag de notícia, papel público global ou catálogo central de mídia. Arquivos pertencem aos próprios modelos que os publicam.

## Portal público

O portal público é renderizado no servidor por Django Templates. As views em `apps/core/web_views.py` consultam o ORM diretamente e renderizam os templates de `backend/templates/portal/`. HTMX atualiza fragmentos da página sem reload e Alpine.js gerencia estado local. A API `/api/v1/` continua disponível para consumo externo.

## Limites atuais

- A Home agrega projetos, notícias, pessoas e métricas do ecossistema, além das configurações do LABTEC.IN.
- Não há endpoint público para memberships nem snapshots de métricas.
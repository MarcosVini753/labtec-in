# Modelagem do banco de dados — Portal LABTEC.IN

Este documento descreve a modelagem consolidada depois do corte institucional e editorial.

## Convenções

- Modelos de domínio usam `id`, `created_at` e `updated_at` por meio de `BaseModel`.
- Registros com página própria usam `slug` único e estável.
- Conteúdos editoriais usam apenas `editorial_status`: `draft`, `in_review`, `published` ou `archived`.
- `published_at` registra a data de publicação, mas não controla visibilidade sozinho.
- Todo conteúdo possui uma única `InstitutionalUnit` obrigatória com `PROTECT`.
- `include_in_parent_ecosystem` permite exibição no recorte público da mãe sem alterar a propriedade.
- Relações com pessoas usam models intermediários quando papel ou ordem pertencem ao vínculo.
- `display_order` existe apenas onde a ordem é estrutural; listas editoriais usam datas e título.

Não existem flags genéricas `is_featured` nem duplicidade entre status e `is_published`. Somente banners e seções institucionais mantêm uma flag simples de publicação por não usarem workflow editorial.

## Institucional

### `InstitutionalUnit`

Representa LABTEC.IN, LATEC e futuras unidades.

Campos principais:

- `name`, `acronym`, `slug` e `unit_type`;
- `parent`, opcional e protegido;
- descrição, missão, visão, imagens e contatos;
- `display_order`.

Toda unidade cadastrada é pública por definição. O modelo não possui flags de ativação ou visibilidade.

LABTEC.IN é `laboratory` sem pai. LATEC é `academic_league` filha do LABTEC.IN. O banco impede autorreferência; `clean()` e `save()` impedem ciclos indiretos nas gravações usuais. `QuerySet.update()` não executa essa validação e deve ser reservado a operações controladas.

### `InstitutionMembership`

Relaciona `Person` e `InstitutionalUnit` com:

- `role` textual;
- `start_date` e `end_date`, opcionais;
- `is_active`, `is_public` e `display_order`.

A combinação `(person, unit, role)` é única e `end_date` não pode anteceder `start_date`. Uma pessoa pode possuir vários papéis na mesma unidade e em unidades diferentes.

## Pessoas e acesso administrativo

### `Person`

Mantém identidade pública, biografia, foto, contatos, ativação e ordenação. Não possui papel global nem flag de destaque. Seus papéis públicos são derivados de memberships ativos e públicos.

### `Profile`

Relaciona opcionalmente um usuário a uma pessoa e define:

- `role`: `lab_coordinator`, `unit_coordinator` ou `mentor`;
- `primary_unit`;
- `authorized_units`;
- `inherit_descendants`;
- `is_active_admin`.

Superusuário é uma capacidade nativa do Django e não um valor de `Profile`.

## Eixos

### `ResearchAxis`

Possui unidade obrigatória, número, título, slug, descrição, palavras-chave, ativação e ordem estrutural. Os sete registros canônicos pertencem à LATEC.

### `AxisMentorship`

Relaciona pessoa e eixo com papel, indicação de mentor principal e ordem. `(axis, person)` é único.

## Pesquisa e trabalhos acadêmicos

### `ResearchProject`

Representa o processo de pesquisa científica.

Campos principais:

- `unit` obrigatória e `axis` opcional;
- `title`, `slug` e `summary`;
- `start_date`, `end_date` e `project_status`;
- `file` e `external_url` opcionais;
- `editorial_status` e `published_at`;
- `include_in_parent_ecosystem`;
- equipe por `ResearchProjectMember`.

`project_status` aceita `planned`, `in_progress`, `completed`, `suspended` e `canceled`. Quando as duas datas existem, `end_date >= start_date` é garantido no modelo e no banco.

### `ResearchProjectMember`

Relaciona pesquisa e pessoa com `role` e `display_order`. Os papéis são coordenador, pesquisador, orientador, bolsista, voluntário e colaborador. O valor `coordinator` é a única fonte da coordenação; não existe booleano duplicado. Cada pessoa aparece no máximo uma vez por pesquisa.

### `AcademicWork`

Representa TCC, monografia, iniciação científica, dissertação, tese ou outro trabalho.

Campos principais:

- `unit` obrigatória e `research_project` opcional;
- `title`, `slug`, `work_type`, curso, instituição e ano;
- `abstract`, palavras-chave, `file` e `external_url`;
- `editorial_status` e `published_at`;
- `include_in_parent_ecosystem`;
- contribuidores por `AcademicWorkContributor`.

### `AcademicWorkContributor`

Relaciona trabalho e pessoa com papel e ordem. Os papéis são autor, orientador, coorientador, avaliador e colaborador. `(academic_work, person, role)` é único.

## Produção científica

### `ScientificOutput`

Representa resultado científico publicável.

Campos principais:

- `unit` obrigatória;
- pesquisa, trabalho acadêmico e eixo opcionais;
- `title`, `slug` e `output_type`;
- `abstract`, `publication_date`, `file` e `external_url`;
- `editorial_status` e `published_at`;
- `include_in_parent_ecosystem`;
- autorias por `ScientificAuthorship`.

Os tipos são artigo, resumo, patente, e-book, livro, relatório técnico e outro. Não existe autoria textual paralela: pessoas cadastradas e ordem são mantidas em `ScientificAuthorship`.

### `ScientificAuthorship`

Relaciona produção e pessoa com `author_order` e `author_role` textual opcional. Pessoa e posição são únicas dentro de cada produção.

## Portfólio

### `Project`

Representa iniciativa prática, produto, serviço, extensão ou solução, e não pesquisa formal.

Possui unidade obrigatória, eixo e classificações práticas opcionais, título, slug, ano, resumo, problema, solução, capa, workflow, `published_at`, `include_in_parent_ecosystem`, equipe, resultados e links.

As categorias históricas `pesquisa` e `producao-cientifica` não existem mais. O projeto de Bioativos que originou uma pesquisa permanece apenas como registro arquivado para rastreabilidade histórica.

`ProjectTeamMember`, `ProjectResult` e `ProjectLink` mantêm `display_order`, pois a sequência faz parte da apresentação do projeto.

## Notícias

### `Post`

Possui unidade obrigatória, eixo opcional, título, slug, resumo, conteúdo, capa, imagem complementar opcional, `editorial_status`, `published_at` e `include_in_parent_ecosystem`.

Notícias não possuem categoria, tags ou autoria própria. O slug é sugerido a partir do título no Admin, permanece editável antes da publicação e não é recalculado automaticamente depois.

### `PostLink`

Relaciona uma notícia a um rótulo e URL externos, com ordenação. O conteúdo da notícia continua sendo texto simples; o portal só converte em link os rótulos cadastrados, sem aceitar HTML editorial livre.

## Aprendizagem

### `Course`

Possui unidade obrigatória, eixo opcional, instrutores, título, slug, descrição, datas, carga horária, situação de inscrições, URL de inscrição, capa, workflow, `published_at` e `include_in_parent_ecosystem`.

### `CourseMaterial`

Pertence a um curso e mantém título, descrição, arquivo, URL externa e ordem estrutural. Não existe flag de visibilidade própria: todos os materiais de um curso publicado são públicos.

Não existem mais `LearningTrack` nem `Event`.

## Transparência

### `TransparencyDocument`

Possui unidade obrigatória, título, slug, tipo, descrição, arquivo, data, processo relacionado, workflow, `published_at` e `include_in_parent_ecosystem`.

## Parcerias e contato

### `Partner`

Relaciona-se a várias unidades por M2M, pois a mesma parceria pode servir simultaneamente ao LABTEC.IN e à LATEC. Mantém tipo, descrição, logo, site, ativação e ordem estrutural.

### `ContactMessage`

Registra tipo, assunto, remetente, organização, texto, situação e data de resposta. Não pertence a uma unidade e seu acesso administrativo é restrito à coordenação do LABTEC.IN e a superusuários.

## Métricas

### `ImpactMetric`

Possui unidade obrigatória, chave, rótulo, valor, sufixo, descrição, ativação e ordem estrutural. `MetricSnapshot` registra valores históricos por data e herda o escopo da métrica.

## Core institucional

`SiteSettings`, `HeroBanner`, `InstitutionalSection` e `SocialLink` possuem unidade obrigatória. Banners, seções e links mantêm ordenação estrutural; banners e seções usam `is_published` simples. A Home consulta somente os registros cujo proprietário é LABTEC.IN.

## Remoções consolidadas

- `people.Role`, `Person.role` e `Person.is_featured`;
- `news.PostCategory`, `news.Tag`, categoria, tags e autores de `Post`;
- `learning.LearningTrack`, `Course.track` e `learning.Event`;
- o app `mediahub`, `MediaAsset` e o catálogo central de mídia;
- flags `is_featured` e `is_published` dos modelos editoriais;
- ordenação manual dos conteúdos editoriais de topo;
- `ResearchProjectMember.is_coordinator`;
- `ScientificOutput.authors`, tipos científicos históricos e campos de proveniência da conversão;
- categorias de portfólio usadas para representar pesquisa e produção científica.

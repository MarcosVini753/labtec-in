# Estrutura institucional do portal LABTEC.IN

## Organização

LABTEC.IN é a instituição raiz. LATEC é uma liga acadêmica filha. Futuras unidades podem ser adicionadas sem criar colunas ou booleanos específicos em cada conteúdo.

```txt
LABTEC.IN (labtec-in)
├── conteúdos próprios do laboratório
├── pessoas e memberships
├── pesquisas, trabalhos, produções e projetos
├── notícias, cursos, transparência e métricas
└── LATEC (latec)
    ├── ligantes e mentores
    ├── sete eixos
    └── conteúdos próprios
```

## Unidades

`InstitutionalUnit` contém nome, sigla, slug, tipo, pai opcional, descrição, identidade visual, contatos e ordem. Toda unidade cadastrada é pública; não existem campos de ativação ou visibilidade no modelo. O banco impede `parent_id == id`; o modelo percorre ancestrais e rejeita ciclos indiretos.

| Nome | Slug | Tipo | Pai |
| --- | --- | --- | --- |
| LABTEC.IN | `labtec-in` | `laboratory` | nenhum |
| LATEC | `latec` | `academic_league` | LABTEC.IN |

`save()` executa validação de hierarquia e o manager bloqueia mudanças inseguras via `bulk_create()` e `bulk_update()`. `QuerySet.update()` é o único bypass ORM conhecido e deve ser usado apenas quando a integridade for garantida explicitamente.

## Memberships

`InstitutionMembership` representa o papel de uma pessoa em uma unidade e período. Contém pessoa, unidade, papel, datas, ativação, visibilidade e ordem.

Exemplo:

| Pessoa | Unidade | Papel |
| --- | --- | --- |
| Marta Adelino | LABTEC.IN | Coordenadora |
| Marta Adelino | LATEC | Coordenadora |
| Marta Adelino | LATEC | Mentor |

`(person, unit, role)` é único e `end_date` não pode anteceder `start_date`. A API de pessoas deriva os papéis públicos dos memberships ativos e públicos; não existe `Person.role`.

As flags do membership pertencem ao vínculo, não à unidade. Assim, a unidade sempre aparece na API, mas um papel de pessoa pode continuar oculto, inativo, ainda não iniciado ou encerrado.

## Propriedade

Todo conteúdo institucional possui uma única unidade obrigatória com `PROTECT`. Isso vale para configurações, banners, seções, links, eixos, projetos, notícias, cursos, pesquisas, trabalhos, produções, transparência e métricas.

Parceiros usam M2M porque uma parceria pode pertencer simultaneamente a várias unidades. Eixo é classificação acadêmica e não substitui a unidade.

## Ecossistema da unidade mãe

Projetos, notícias, cursos, pesquisas, trabalhos acadêmicos, produções científicas e documentos de transparência possuem `include_in_parent_ecosystem`.

Ao consultar `?unit=<slug>`, a API retorna:

- conteúdo próprio da unidade consultada;
- conteúdo de suas filhas diretas com a opção habilitada.

Não há propagação recursiva. Um conteúdo de uma neta não aparece no recorte da avó por essa regra, e o conteúdo continua serializando a filha como proprietária.

Exemplo: uma notícia da LATEC com a opção habilitada aparece tanto em `?unit=latec` quanto em `?unit=labtec-in`. Ela continua pertencendo somente à LATEC.

A Home é uma exceção deliberada: usa somente configurações, banners, seções e links diretamente do LABTEC.IN e ignora a agregação editorial.

## Escopo administrativo

- Superusuário: todas as unidades.
- Coordenação do LABTEC.IN: raiz, descendentes e publicação final.
- Coordenação de unidade: unidades autorizadas e descendentes apenas quando habilitados, sem publicação final.
- Mentor: LATEC e apenas os próprios eixos, sem publicação final.

O acesso administrativo a descendentes é uma permissão do perfil; a inclusão pública no ecossistema é uma decisão do conteúdo. São mecanismos distintos.

## Estado do corte

Unidades obrigatórias e sempre públicas, memberships com visibilidade própria, filtros com agregação de um nível e remoção de `Person.role` estão consolidados. O portal público server-rendered atende às seções descritas neste documento. A Home já agrega projetos, notícias, pessoas e métricas do ecossistema.

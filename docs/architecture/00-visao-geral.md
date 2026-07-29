# Visão geral da arquitetura — Portal LABTEC.IN

O LABTEC.IN — Laboratório de Biotecnologia, Biodiversidade e Inovação — é a instituição raiz, proprietária do portal, do backend e dos conteúdos institucionais.

A LATEC é uma liga acadêmica vinculada ao LABTEC.IN. Ela é uma unidade filha e uma seção do mesmo portal, não uma aplicação independente.

## Estado implementado

O portal público é renderizado no servidor por Django Templates, com HTMX para atualizações parciais e Alpine.js para estado local. O backend Django oferece Django REST Framework, Django Admin e API `/api/v1/`. O backend organiza identidade institucional, pessoas, eixos, pesquisas, trabalhos acadêmicos, portfólio, produção científica, notícias, cursos, transparência, parcerias e métricas.

As views em `apps/core/web_views.py` consultam o ORM diretamente e renderizam os templates de `backend/templates/portal/`. A API `/api/v1/` continua disponível para consumo externo e como endpoint do HTMX quando conveniente. Um frontend estático em JavaScript puro existiu como protótipo, mas não é mais necessário para testar ou operar o portal.

O app `institutional` modela LABTEC.IN como raiz e LATEC como filha. O seed cria 43 memberships, associa os sete eixos e os nove mentores à LATEC e classifica os conteúdos iniciais por unidade. Hierarquia e memberships possuem validações no modelo e no banco.

Toda unidade cadastrada é pública por definição; `InstitutionalUnit` não possui estados de ativação ou ocultação. A exposição de uma pessoa continua sendo controlada separadamente pelos campos e datas de seu membership.

Todo conteúdo institucional possui `unit` obrigatória. Parceiros são a exceção de cardinalidade: podem se relacionar com mais de uma unidade. A API aceita `?unit=<slug>` e pode agregar conteúdo de filhas diretas que tenha optado pelo ecossistema da mãe.

## Estrutura institucional

```txt
LABTEC.IN
├── conteúdos institucionais do laboratório
├── pessoas e memberships
├── pesquisas e trabalhos acadêmicos
├── produções científicas
├── projetos e soluções
├── notícias e cursos
├── transparência, parceiros e métricas
└── LATEC
    ├── ligantes e mentores
    ├── sete eixos de atuação
    └── conteúdos próprios da Liga
```

Cada registro tem uma única unidade proprietária. A opção `include_in_parent_ecosystem` controla apenas sua presença no recorte público da mãe; ela não transfere propriedade nem cria copropriedade.

## Objetivo do backend

Atuar como CMS institucional e API pública, permitindo administrar:

- identidade, missão, visão, histórico e canais institucionais;
- pessoas e seus vínculos por unidade;
- pesquisas, TCCs, trabalhos e produções científicas;
- projetos, soluções, notícias e cursos;
- transparência, parceiros, métricas e mensagens de contato;
- conteúdo específico da LATEC, seus ligantes, mentores e eixos.

## Áreas públicas

- Home direta do LABTEC.IN.
- Institucional, pessoas e unidades.
- Pesquisas e trabalhos acadêmicos.
- Produções científicas.
- Portfólio de soluções e iniciativas práticas.
- Notícias e cursos.
- Transparência, parceiros e contato.
- Seção LATEC com seus vínculos, eixos e conteúdos.

## Eixos de atuação

Os sete eixos pertencem à LATEC e organizam prioritariamente as atividades da Liga. Pesquisas ou conteúdos de outra unidade podem se relacionar com um eixo quando houver vínculo acadêmico explícito; eixo não substitui unidade.

## Regras consolidadas

- LABTEC.IN é raiz; LATEC é filha.
- Uma pessoa pode possuir múltiplos memberships na mesma unidade ou em unidades diferentes.
- Todo conteúdo possui uma unidade proprietária obrigatória protegida por `PROTECT`.
- A Home usa somente configurações, banners, seções e links diretamente do LABTEC.IN.
- Todos os materiais de um curso publicado são públicos; materiais não possuem visibilidade própria.
- `?unit=<slug>` retorna a unidade consultada e, em um único nível, conteúdos de filhas diretas marcados para integrar seu ecossistema.
- O workflow editorial usa apenas `draft`, `in_review`, `published` e `archived`.
- Somente superusuários e a coordenação do LABTEC.IN publicam, arquivam, excluem ou alteram conteúdo final.
- Coordenadores de unidade e mentores atuam em rascunhos e revisões dentro do próprio escopo.
- Slugs identificam páginas públicas e o frontend deve usar os valores entregues pela API. Os dois slugs históricos com `latecin` foram substituídos sem redirecionamento.

O portal público é server-rendered pelo Django; não há frontend separado em produção. A Home agrega projetos, notícias, pessoas e métricas do ecossistema, além das configurações, banners e seções do LABTEC.IN.

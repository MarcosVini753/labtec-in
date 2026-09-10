# Documentação técnica — Portal LABTEC.IN

Esta pasta documenta a arquitetura do portal do LABTEC.IN — Laboratório de Biotecnologia, Biodiversidade e Inovação.

O LABTEC.IN é a instituição raiz e proprietária do portal. A LATEC é uma unidade filha do tipo liga acadêmica, apresentada dentro do mesmo backend e da mesma API.

## Estado consolidado

O backend Django implementa:

- unidades hierárquicas e memberships institucionais;
- unidades sempre públicas, sem estados próprios de ativação ou ocultação;
- unidade proprietária obrigatória nos conteúdos;
- escopo administrativo por unidade, descendência e eixo;
- workflow editorial único por `editorial_status`;
- inclusão opcional de conteúdo de uma filha no ecossistema da mãe;
- pesquisas, trabalhos acadêmicos, produção científica e portfólio como domínios distintos;
- API pública versionada em `/api/v1/`;
- seed idempotente com 43 memberships, sete eixos da LATEC e a pesquisa de Bioativos publicada.

Materiais de curso não possuem visibilidade independente: quando o curso está publicado, todos os seus materiais são públicos.

O corte definitivo removeu papéis públicos globais, papéis administrativos redundantes, categorias, tags e autoria de notícias, trilhas, eventos, o catálogo MediaHub, flags de destaque, a duplicidade de publicação e categorias históricas de pesquisa no portfólio. O projeto legado de Bioativos foi arquivado após a publicação do registro em `research`.

## Estrutura

```txt
docs/
  README.md
  architecture/
    00-visao-geral.md
    01-modulos.md
    02-modelagem-banco.md
    03-api-publica.md
    04-permissoes.md
    05-deploy.md
    06-eixos-de-atuacao.md
    07-workflow-editorial.md
    08-seed-e-fixtures.md
    09-transparencia-e-repositorio.md
    10-estrutura-institucional.md
    11-pesquisas-e-trabalhos-academicos.md
    12-migracao-labtec.md
    diagrams/
      c4-context.md
      c4-container.md
      erd.md
      module-map.md
  adr/
    0001-usar-django-e-drf.md
    ...
    0015-separar-pesquisas-tccs-portfolio.md
    0016-simplificar-conteudo-e-cortar-legados.md
```

## Mapa de leitura

- [Visão geral](architecture/00-visao-geral.md): contexto institucional e regras consolidadas.
- [Módulos](architecture/01-modulos.md): responsabilidades e dependências dos apps.
- [Modelagem](architecture/02-modelagem-banco.md): entidades e relações atuais.
- [API pública](architecture/03-api-publica.md): endpoints, filtros e agregação institucional.
- [Permissões](architecture/04-permissoes.md): papéis administrativos e escopos.
- [Estrutura institucional](architecture/10-estrutura-institucional.md): LABTEC.IN, LATEC, hierarquia e ecossistema.
- [Pesquisas e trabalhos acadêmicos](architecture/11-pesquisas-e-trabalhos-academicos.md): pesquisa, trabalho, produção e portfólio.
- [Migração](architecture/12-migracao-labtec.md): preflights, corte dos legados e operação segura.

## Direção técnica

- Django e Django REST Framework.
- Django Admin como CMS inicial.
- `User` padrão do Django e perfis institucionais mínimos.
- PostgreSQL em homologação e produção; SQLite no desenvolvimento local.
- arquivos nos campos dos próprios domínios e volumes persistentes fora do desenvolvimento.
- navegação por slugs devolvidos pela API e API mantida em `/api/v1/`.

O corte final corrigiu dois slugs de notícias que continham `latecin`; as URLs antigas não possuem alias nem redirecionamento. O frontend deve sempre usar o slug recebido da API.



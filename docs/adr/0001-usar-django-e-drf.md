# ADR 0001: Usar Django e Django REST Framework

## Status

Aceita

## Contexto

O portal do LABTEC.IN precisa gerenciar conteúdos do Laboratório de Biotecnologia, Biodiversidade e Inovação e de suas unidades filhas, incluindo a LATEC.

O repositório possui backend Django já implementado. A arquitetura requer persistência, administração institucional, workflow editorial e API pública `/api/v1/`. O portal público é renderizado no servidor por Django Templates, com HTMX para atualizações parciais e Alpine.js para estado local. Um frontend estático em HTML, CSS e JavaScript puro existiu como protótipo e cliente SPA da API, mas não é mais necessário para testar ou operar o portal.

## Decisão

Usar Django como framework backend e Django REST Framework para a API pública do portal LABTEC.IN.

A LATEC será modelada como unidade institucional dentro do mesmo backend e da mesma API.

## Alternativas consideradas

- Django e Django REST Framework.
- Node.js com Express ou NestJS.
- Laravel.
- CMS pronto ou headless CMS.

## Consequências positivas

- ORM, migrations, autenticação, permissões e Django Admin integrados.
- Evolução incremental da API.
- Administração de conteúdos do laboratório e de unidades filhas.
- Portal público server-rendered pelo próprio Django, sem necessidade de frontend separado.
- HTMX e Alpine.js fornecem interatividade sem transformar o portal em um SPA.
- A API `/api/v1/` continua disponível para consumo externo e integração com outros clientes.

## Riscos e cuidados

- Manter apps, serializers, permissões e migrations organizados.
- Aplicar escopo institucional sem duplicar backends por unidade.
- Configurar o Django Admin com filtros, buscas e permissões adequadas.

# ADR 0017: Adotar Django Templates como frontend principal

## Status

Aceita.

## Contexto

O portal foi inicialmente projetado com um frontend estático em HTML, CSS e JavaScript puro (`latec-app/`) que consumia a API REST `/api/v1/` como SPA. Esse frontend exigia um servidor HTTP separado (ex: `python -m http.server 5500`), duplicava regras de roteamento e não tinha acesso direto às validações do backend.

Com a maturidade do backend Django — models, admin, workflow editorial, escopo institucional e API — tornou-se mais eficiente renderizar o portal público diretamente no servidor com Django Templates, HTMX e Alpine.js, eliminando a necessidade de um frontend separado para operar e testar a aplicação.

## Decisão

Adotar Django Templates (DTL) como frontend principal do portal público, com HTMX para requisições parciais e Alpine.js para estado local no navegador.

- As views em `apps/core/web_views.py` consultam o ORM diretamente e renderizam templates de `backend/templates/portal/`.
- `base.html` é o esqueleto comum; cada página estende esse base.
- HTMX atualiza fragmentos da página sem reload (busca em catálogos, formulário de contato, dashboard administrativo).
- Alpine.js gerencia estado local (filtros de perfis, menu mobile).
- A API `/api/v1/` continua existindo para consumo externo, integração com outros clientes e como endpoint do HTMX quando conveniente.
- O frontend estático `latec-app/` deixa de ser necessário para testar ou operar o portal.

## Alternativas consideradas

- Manter o frontend SPA em JavaScript puro consumindo a API.
- Adotar um framework SPA (React, Vue) com build step.
- Usar um CMS headless com frontend separado.

## Consequências positivas

- Portal público servido por um único processo (Django), sem servidor frontend separado.
- Regras de publicação, permissões e escopo institucional aplicados no servidor, sem duplicação no cliente.
- Templates herdados e partials reduzem código repetido.
- HTMX fornece interatividade sem o custo de um SPA.
- A API REST permanece disponível para integrações externas.
- Testes do portal são feitos diretamente com `python manage.py runserver`.

## Consequências negativas e riscos

- A renderização do portal depende do Django; não há mais separação física entre frontend e backend.
- Templates server-rendered não são adequados para interatividade complexa de SPA; HTMX e Alpine.js cobrem o espectro necessário, mas têm limites.
- O CSS e os assets estáticos do portal são servidos pelo Django (`collectstatic` em produção).
- O frontend estático `latec-app/` pode ser mantido como referência ou cliente alternativo da API, mas não é mais o caminho principal.

## Relação com outros ADRs

Esta decisão complementa o ADR 0001 (Django + DRF) ao estabelecer que o portal público é renderizado pelo próprio Django, não por um cliente separado. Não substitui a API `/api/v1/`, que continua como contrato público versionado.
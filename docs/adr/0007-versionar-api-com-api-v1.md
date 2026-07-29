# ADR 0007: Versionar API pública com /api/v1/

## Status

Aceita

## Contexto

O portal público server-rendered consulta o ORM diretamente via `web_views.py`. A API `/api/v1/` é consumida por clientes externos e pelo HTMX para requisições parciais. A API precisa de prefixo explícito e consistente.

A versão inicial ainda está em desenvolvimento e não possui consumidores externos estáveis conhecidos.

## Decisão

Manter todos os endpoints públicos sob `/api/v1/`.

As mudanças institucionais de LABTEC.IN e LATEC serão evoluídas nessa versão antes da estabilização pública; nenhuma nova versão será aberta nesta etapa documental.

## Consequências positivas

- Roteamento e documentação consistentes.
- Evolução da arquitetura institucional sem duplicar endpoints.
- Base explícita para versionamento futuro quando houver contrato público estável.

## Riscos e cuidados

- Não criar endpoints públicos fora de `/api/v1/`.
- Atualizar OpenAPI e consumidores a cada evolução.
- Planejar versão futura apenas quando houver incompatibilidade após estabilização.
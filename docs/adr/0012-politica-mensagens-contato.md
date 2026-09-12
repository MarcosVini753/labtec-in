# ADR 0012: Política inicial para mensagens de contato

## Status

Substituída pela [ADR 0019](0019-compartilhar-caixa-de-contato-entre-coordenacoes.md).

## Contexto

O formulário público de contato do portal LABTEC.IN coleta nome, e-mail, assunto, tipo de contato e mensagem. Esses dados não são públicos.

## Decisão

Na fase inicial:

- mensagens serão armazenadas por tempo indeterminado;
- o acesso funcional será restrito à coordenação do LABTEC.IN;
- coordenadores de unidades filhas não receberão acesso automático;
- superusuários técnicos poderão ter acesso operacional ao admin ou banco.

## Consequências positivas

- Gestão inicial simples.
- Menor exposição de dados pessoais.
- Rastreabilidade dos contatos recebidos pelo laboratório.

## Riscos e cuidados

- Revisar futuramente a política de retenção.
- Aplicar o escopo institucional no Django Admin.
- Distinguir acesso técnico de autorização funcional de uso.

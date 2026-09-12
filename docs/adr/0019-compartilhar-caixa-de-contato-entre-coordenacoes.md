# ADR 0019: Compartilhar a caixa de contato entre coordenações

## Status

Aceita.

## Contexto

As mensagens enviadas pelo formulário público contêm dados pessoais e precisam permanecer rastreáveis. A política inicial restringia toda a caixa à coordenação do LABTEC.IN, mas as coordenações das unidades também precisam acompanhar e registrar o atendimento dos contatos recebidos pelo portal.

O formulário não identifica uma unidade destinatária, portanto não existe informação confiável para separar automaticamente as mensagens por escopo institucional.

## Decisão

- superusuários, coordenação do LABTEC.IN e coordenações de unidades compartilham a mesma caixa de entrada;
- coordenadores de unidade podem ler todas as mensagens e alterar somente o status e a data de atendimento;
- coordenadores de unidade não podem criar nem excluir mensagens;
- mentores não recebem acesso às mensagens;
- o formulário apenas armazena os contatos no banco, sem envio de e-mail ou notificação.

## Consequências

- as coordenações conseguem acompanhar o atendimento sem depender da conta técnica;
- dados pessoais ficam expostos a mais coordenadores, que devem tratá-los somente para a finalidade do contato;
- o histórico enviado pelo visitante permanece imutável para coordenadores de unidade;
- um futuro roteamento por unidade exigirá adicionar uma escolha explícita e validada ao formulário.

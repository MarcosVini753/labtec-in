# ADR 0018: Usar bootstrap único para o conteúdo canônico de produção

## Status

Aceita

## Contexto

O portal possui conteúdo inicial institucional, incluindo pessoas, projetos, notícias, imagens e materiais. Após a implantação, a coordenação precisa administrar esse conteúdo pelo Django Admin sem que uma atualização de código reverta decisões editoriais ou arquivos enviados.

## Decisão

`seed_initial_data` inicializa somente uma base vazia. Ele valida os ativos versionados em `backend/seed_assets/`, cria os registros canônicos e copia seus arquivos para o `MEDIA_ROOT` persistente.

Quando a unidade raiz `labtec-in` já existe, o comando falha sem modificar banco ou mídia. Depois do bootstrap, o Django Admin é a fonte de verdade para conteúdo, imagens e workflow editorial.

O primeiro deploy executa migrations, bootstrap, coleta de estáticos e criação do administrador. Deploys seguintes não executam o seed. Dados de borda e contas de teste continuam fora de produção.

## Consequências

- Conteúdo e imagens iniciais são reproduzíveis em uma instalação nova.
- Alterações administrativas não são sobrescritas por deploys futuros.
- O volume de mídia e o PostgreSQL precisam de backup coordenado.
- Um ativo canônico ausente bloqueia a inicialização até que o arquivo oficial seja incluído.

## Relação com ADRs anteriores

Esta decisão substitui a reexecução idempotente do conteúdo canônico prevista no ADR 0013. A idempotência permanece aplicável apenas aos dados de borda de desenvolvimento e homologação.

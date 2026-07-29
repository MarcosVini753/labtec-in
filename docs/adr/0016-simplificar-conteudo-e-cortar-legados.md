# ADR 0016: Simplificar conteúdo editorial e cortar legados

## Status

Aceita.

## Contexto

A migração institucional criou unidades, escopo administrativo e domínios próprios para pesquisa e trabalhos acadêmicos. Depois do backfill, o backend ainda mantinha duplicidades e estruturas sem uso comprovado: papéis administrativos sobrepostos, papel público global, dois controles de publicação, flags de destaque, taxonomias de notícia, trilhas, eventos e um MediaHub sem relações com os conteúdos.

Também era necessário decidir como conteúdos de uma unidade filha participariam do portal da mãe sem transformar a propriedade institucional em uma relação muitos-para-muitos.

## Decisão

- manter apenas superusuário, `lab_coordinator`, `unit_coordinator` e `mentor` no acesso administrativo;
- representar papéis públicos exclusivamente por `InstitutionMembership`;
- tornar a unidade proprietária obrigatória e única nos conteúdos;
- tornar toda unidade cadastrada automaticamente pública, sem flags próprias de ativação ou visibilidade;
- permitir opt-in no ecossistema da mãe direta por `include_in_parent_ecosystem`, sem agregação recursiva;
- usar somente `editorial_status` para visibilidade dos conteúdos editoriais;
- remover flags de destaque e ordenação manual dos conteúdos editoriais de topo;
- simplificar notícias para conteúdo, resumo, capa, eixo, unidade e workflow;
- manter somente cursos e materiais em `learning`, tornando públicos todos os materiais de um curso publicado;
- manter arquivos nos próprios domínios e remover integralmente app, tabela, ContentType e permissões do MediaHub;
- reduzir pesquisas a metadados de catálogo, arquivo/URL, equipe e workflow;
- manter trabalhos e produções com metadados bibliográficos, arquivo/URL e autoria estruturada;
- concluir o corte das categorias históricas, publicar Bioativos como pesquisa e arquivar sua origem no portfólio;
- retirar fallbacks residuais de nome, unidade nula e workflow;
- corrigir os dois slugs de notícias que continham `latecin`, sem alias ou redirecionamento.

Esta decisão supera o ADR 0006. Os demais ADRs permanecem como registro das decisões e etapas anteriores.

## Consequências positivas

- Menos estados contraditórios e menos campos administrativos.
- Propriedade institucional inequívoca.
- Contratos públicos menores.
- Pesquisa, trabalho, produção e portfólio com responsabilidades claras.
- Agregação institucional sem copropriedade.
- Menos models e telas sem uso atual.

## Consequências negativas e riscos

- Mudança incompatível dentro da API v1, exigindo atualização de clientes externos que consomem a API.
- O portal público server-rendered não foi impactado, pois consulta o ORM diretamente via `web_views.py`.
- Migrations destrutivas dependem de backup e preflight.
- A limpeza de arquivos órfãos é destrutiva e depende de inventário e backup prévios.
- Autores externos precisam ser cadastrados como pessoas para integrar a autoria estruturada.
- O opt-in alcança somente a mãe direta; hierarquias que precisem de agregação recursiva exigirão nova decisão.

## Migração

As migrations validam unidades ausentes, publicação contraditória, papéis sem membership, autores textuais e conversões históricas antes de remover campos. Perfis de papéis retirados são desativados, sem promoção automática.

O app e a tabela MediaHub são removidos por migration segura para instalações novas ou atualizadas. O comando `cleanup_orphan_media` produz o inventário no terminal por padrão e só exclui arquivos com `--delete`; raízes personalizadas exigem a confirmação explícita do caminho absoluto. Não existe registro operacional persistente do corte.

Os slugs públicos continuam sendo a identidade das páginas, mas duas correções são deliberadamente incompatíveis: as ocorrências de `latecin` nas notícias foram substituídas por `latec`, e as URLs antigas retornam `404`.

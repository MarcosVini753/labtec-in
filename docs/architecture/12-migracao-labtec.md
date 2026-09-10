# Migração e corte institucional do LABTEC.IN

Este documento registra a sequência aplicada para consolidar LABTEC.IN como raiz, LATEC como filha e remover os legados editoriais.

## Resultado

- LABTEC.IN e LATEC usam os slugs públicos `labtec-in` e `latec`.
- Toda unidade cadastrada é pública; os antigos estados de ativação e visibilidade da unidade foram removidos.
- Todo conteúdo possui unidade obrigatória com `PROTECT`.
- O seed mantém 43 memberships, sete eixos e nove mentores sem duplicação.
- Pessoas públicas usam memberships; `Person.role` e `people.Role` foram removidos.
- Perfis administrativos usam somente `lab_coordinator`, `unit_coordinator` e `mentor`.
- O workflow editorial usa somente `editorial_status`.
- Conteúdo de uma filha pode optar pelo ecossistema da mãe direta.
- Pesquisa, trabalho acadêmico, produção científica e portfólio são domínios separados.
- Notícias, cursos e arquivos foram simplificados.
- Todos os materiais de um curso publicado são públicos e não possuem flag própria.
- O app, a tabela, o ContentType e as permissões do MediaHub foram removidos.
- Bioativos é uma pesquisa publicada e seu projeto legado está arquivado.

## Preflights

As migrations de corte falham com IDs claros antes de modificar o schema quando encontram:

- memberships duplicados ou períodos inválidos;
- ciclos diretos ou indiretos de unidades;
- conteúdos sem unidade;
- contradição entre o status editorial e o antigo `is_published`;
- papel público sem membership equivalente;
- produção científica com autores textuais ainda não convertidos;
- projeto histórico de pesquisa/produção sem registro de destino.

Essas verificações não inferem nem apagam dados para corrigir inconsistências.

Atualização *in-place* de uma base populada anterior ao corte não é suportada. Em desenvolvimento, teste e homologação, descarte a base configurada e inicialize-a vazia antes de aplicar as migrations e o seed; o preflight permanece como proteção contra uma migração acidental de conteúdo legado sem unidade.

## Papéis e pessoas

Perfis `admin`, `editor` e `reader` foram tecnicamente convertidos para `unit_coordinator`, desativados e retirados do Django Admin quando o usuário não era superusuário. Nenhum perfil foi promovido automaticamente.

Antes de remover `Person.role`, a migration confirmou que o papel histórico tinha membership institucional equivalente. A API de pessoas passou a serializar apenas memberships públicos ativos.

## Unidade obrigatória

Em uma base recriada, `unit` é obrigatória em:

- configurações, banners, seções e links sociais;
- eixos;
- projetos, notícias e cursos;
- pesquisas, trabalhos e produções científicas;
- documentos de transparência;
- métricas.

Parceiros continuam com várias unidades. `PROTECT` evita excluir uma unidade ainda referenciada.

## Workflow e contratos

O corte normalizou os campos antigos `status` para `editorial_status`, confirmou sua equivalência com `is_published` e removeu a flag duplicada. Flags de destaque e ordenação manual dos conteúdos editoriais de topo também foram removidas.

Antes de retirar `ResearchProjectMember.is_coordinator`, valores verdadeiros foram convertidos para o papel `coordinator`. Assim, a informação de coordenação permanece no campo `role`, que passa a ser sua única fonte.

Notícias perderam categoria, tags e autores. Cursos perderam trilha; trilhas e eventos foram apagados. Materiais passaram a herdar integralmente a publicação do curso.

O app MediaHub foi retirado de `INSTALLED_APPS` e do repositório. Uma migration final remove a tabela residual, o ContentType e as permissões tanto em instalações atualizadas quanto em bancos novos. O histórico de migrations aplicadas permanece no Django e não constitui compatibilidade em execução.

## Conversão científica

Projetos das categorias históricas foram associados aos destinos já convertidos. Estado de publicação e `published_at` foram transferidos quando aplicável, e as origens de portfólio foram arquivadas e desvinculadas das categorias antigas.

Para Bioativos:

1. a pesquisa nova preservou slug, unidade, eixo, resumo e equipe compatíveis;
2. o papel do líder foi convertido para `coordinator`;
3. a pesquisa foi publicada mesmo sem arquivo;
4. o projeto de portfólio foi arquivado;
5. o identificador de proveniência e as categorias históricas foram removidos.

Em banco novo, o seed cria somente a pesquisa publicada. Em banco atualizado, ele não republica o projeto legado.

## Ordem operacional

1. Em desenvolvimento, teste ou homologação, descartar a base configurada e os arquivos de mídia de teste.
2. Aplicar todas as migrations em uma base vazia.
3. Executar `seed_initial_data` uma vez.
4. Executar `check`, testes, verificação de drift e validação OpenAPI.
5. Revisar manualmente conteúdos, autorias e arquivos publicados.

O procedimento suportado pressupõe dados descartáveis. Se uma base tiver conteúdo a preservar, não aplique este corte nela.

## Contratos mantidos e quebras intencionais

- `/api/v1/` e os endpoints principais permanecem.
- `HeroBanner` e `InstitutionalSection` mantêm sua flag simples de publicação.
- Ordem estrutural permanece em equipes, autorias, materiais, resultados, links, banners, seções, eixos, memberships, métricas e parceiros.

As compatibilidades residuais de nomes institucionais, unidade nula e status editorial foram removidas. Dois slugs de notícias foram corrigidos de `latecin` para `latec`; as URLs antigas retornam `404`, sem alias ou redirecionamento. Os demais slugs públicos não foram modificados por este corte.

Arquivos órfãos foram inventariados e excluídos explicitamente pelo comando de manutenção. Não foi criado registro operacional persistente do corte.

## Fora do escopo

- frontend;
- expansão da Home;
- autenticação pública;
- permissões institucionais na API anônima;
- infraestrutura ou storage externo.

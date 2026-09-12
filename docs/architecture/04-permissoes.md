# Permissões administrativas do portal LABTEC.IN

O sistema usa o `User` padrão do Django, o Django Admin e um `accounts.Profile` para definir escopo institucional. Pessoas públicas continuam independentes de usuários administrativos.

## Papéis administrativos

Além do superusuário nativo, existem somente:

- `lab_coordinator`: coordenação do LABTEC.IN;
- `unit_coordinator`: coordenação de uma unidade;
- `mentor`: mentor da LATEC.

Os antigos papéis customizados `admin`, `editor` e `reader` foram removidos. Perfis com esses valores foram convertidos tecnicamente para `unit_coordinator`, desativados com `is_active_admin=False` e tiveram `is_staff` removido quando o usuário não era superusuário. A reativação exige uma decisão administrativa explícita.

## Escopo do perfil

`Profile` mantém:

- `person`, opcional;
- `primary_unit`, opcional;
- `authorized_units`, opcional;
- `inherit_descendants`;
- `role`;
- `is_active_admin`.

Perfil inativo, sem escopo aplicável ou usuário sem acesso ao Admin não recebe permissão institucional.
O formulário administrativo de usuário impede habilitar um não-superusuário como membro da equipe sem um perfil administrativo ativo e válido.

## Matriz

| Papel | Escopo | Criar e revisar | Publicar, arquivar, excluir ou alterar conteúdo final |
| --- | --- | --- | --- |
| Superusuário | Todas as unidades | Sim | Sim |
| `lab_coordinator` | LABTEC.IN e todos os descendentes | Sim | Sim |
| `unit_coordinator` | Unidade principal, autorizadas e descendentes quando habilitados | Sim, em rascunho/revisão | Não |
| `mentor` | LATEC e somente os eixos em que possui `AxisMentorship` | Sim, em rascunho/revisão | Não |

Somente superusuários e a coordenação do LABTEC.IN realizam a publicação final.

## Proteções do Admin

O escopo é aplicado em:

- querysets de conteúdo e de filhos;
- escolhas de unidade e eixo em formulários;
- autocomplete;
- inlines;
- validação do objeto submetido, inclusive POST adulterado;
- ações de publicação e arquivamento.

Coordenadores de unidade e mentores não alteram registros publicados. Eles podem definir `include_in_parent_ecosystem` em rascunho ou revisão; a publicação pela coordenação do LABTEC.IN aprova simultaneamente o conteúdo e essa opção.

Regras especiais:

- mentor acessa apenas objetos relacionados aos próprios eixos;
- parceiro ligado a várias unidades é editável somente por superusuário ou coordenação do LABTEC.IN;
- mensagens de contato formam uma caixa compartilhada entre superusuários, coordenação do LABTEC.IN e coordenações de unidades; coordenadores de unidade alteram somente o status e a data de atendimento, sem criar ou excluir mensagens, e mentores não recebem acesso;
- usuários, perfis e unidades são geridos somente por superusuário;
- coordenação do LABTEC.IN pode gerir memberships, mas não elevar privilégios administrativos.

Unidades institucionais não possuem estado privado ou inativo: toda unidade cadastrada aparece publicamente. Essa regra não torna memberships automaticamente públicos; cada vínculo continua sujeito a `is_active`, `is_public` e ao seu período de validade.

Materiais não têm autorização ou publicação próprias. O escopo administrativo vem do curso e todos os materiais do curso tornam-se públicos quando ele é publicado.

A API pública permanece anônima, read-only para catálogos e independente dos escopos administrativos.

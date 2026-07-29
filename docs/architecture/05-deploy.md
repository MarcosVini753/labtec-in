# Deploy e ambientes do portal LABTEC.IN

O backend Django serve o portal público server-rendered (Django Templates + HTMX + Alpine.js), a API REST `/api/v1/` e o Django Admin. O mesmo backend atende o LABTEC.IN e suas unidades, incluindo a seção LATEC. Não há frontend separado para implantar — o portal é servido pelo próprio Django.

## Ambientes previstos

### Desenvolvimento local

- SQLite permitido no início.
- `DEBUG=True`.
- arquivos locais para mídia.
- CORS liberado apenas para o frontend local (se houver cliente externo).
- mídia em diretório local por `MEDIA_ROOT`.

### Homologação

- PostgreSQL.
- `DEBUG=False`.
- domínio ou subdomínio de teste a definir.
- dados próximos da produção.
- validação do fluxo administrativo, escopo institucional e API.
- mídia em volume persistente no servidor.

### Produção institucional

- PostgreSQL.
- HTTPS obrigatório.
- variáveis de ambiente.
- backups.
- configuração de arquivos estáticos e mídia.
- domínio institucional quando definido.
- mídia em volume persistente no servidor inicialmente.

Nenhum domínio definitivo é estabelecido por esta documentação.

## Stack

- Django.
- Django REST Framework.
- PostgreSQL em homologação e produção.
- SQLite apenas no desenvolvimento local inicial.
- `django-environ` ou alternativa equivalente para variáveis de ambiente.
- `django-cors-headers` para CORS.
- `Pillow` para campos de imagem.
- `drf-spectacular` para OpenAPI.
- servidor WSGI ou ASGI conforme a estratégia de implantação.
- HTMX e Alpine.js via CDN nos templates do portal.

## Portal público

O portal público é renderizado pelo próprio Django. As views em `apps/core/web_views.py` consultam o ORM diretamente e renderizam os templates de `backend/templates/portal/`. HTMX faz requisições parciais para atualizar fragmentos da página sem reload; Alpine.js gerencia estado local no navegador.

Em produção, os assets estáticos (CSS, JS, imagens) são servidos via `collectstatic` para o diretório configurado em `STATIC_ROOT`. A mídia enviada pelos usuários é servida do diretório configurado em `MEDIA_ROOT`.

## Política de mídia

- Desenvolvimento: armazenamento local.
- Homologação: volume persistente no servidor.
- Produção: volume persistente no servidor inicialmente.

A migração futura para storage externo poderá ser avaliada se houver crescimento relevante, necessidade de CDN ou requisito institucional.

LABTEC.IN e LATEC compartilham a mesma infraestrutura de mídia. Cada arquivo pertence diretamente ao modelo de domínio que o publica; não existe catálogo central MediaHub nem separação física por unidade.

## Configurações mínimas de produção

- `DEBUG=False`.
- `ALLOWED_HOSTS` configurado.
- origens confiáveis configuradas.
- CORS restrito aos domínios esperados.
- banco configurado por variável de ambiente.
- arquivos estáticos coletados por `collectstatic`.
- volume de mídia persistente e com backup.
- segredos fora do repositório.

## Backups

A produção deve possuir política mínima de backup para:

- PostgreSQL;
- arquivos de mídia;
- configurações de ambiente;
- procedimento testado de restauração.

## Migração institucional

Os apps `institutional` e `research` não exigem novos containers. Antes do corte, a implantação deve fazer backup e executar os preflights de unidade, workflow, autoria e papéis públicos. Depois, aplica as migrations incrementais, executa o seed idempotente duas vezes e valida API e OpenAPI. As migrations removem estruturas e dados legados e não possuem reversão integral.

O app `mediahub`, sua tabela, ContentType e permissões foram removidos. Arquivos permanecem no volume compartilhado e são relacionados diretamente pelos modelos de domínio.

O comando abaixo inventaria arquivos sem referência sem alterar o storage:

```bash
python manage.py cleanup_orphan_media
```

Depois de revisar a lista e confirmar o backup, a exclusão permanente é explícita:

```bash
python manage.py cleanup_orphan_media --delete
python manage.py cleanup_orphan_media
```

O comando acima é suficiente para o caminho padrão `backend/media`. Se `MEDIA_ROOT` apontar
para um volume personalizado, a exclusão exige confirmar exatamente a raiz inventariada:

```bash
python manage.py cleanup_orphan_media --delete --confirm-root=/caminho/absoluto/da/midia
```

A última execução deve informar zero órfãos. O inventário é exibido no terminal; não existe tabela, arquivo de relatório ou registro operacional permanente do corte.

## Premissas

A implantação final deve considerar domínio institucional, HTTPS, backups, controle de ambiente, persistência de mídia e processo claro de atualização, sem criar infraestrutura separada para a LATEC.
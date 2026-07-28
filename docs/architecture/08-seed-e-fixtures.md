# Seed e fixtures do portal LABTEC.IN

O comando idempotente é:

```txt
python manage.py seed_initial_data
```

Para dados de borda de desenvolvimento e homologação, execute depois:

```bash
python manage.py seed_edge_case_data --password senha-de-teste
```

Esse comando é idempotente e cria casos de teste para hierarquia, vínculos institucionais, workflow editorial, parceiros, mensagens, links sociais, snapshots de métricas e perfis administrativos. Unidades institucionais continuam públicas por decisão de domínio; os casos de visibilidade são representados por vínculos e estados editoriais.

Ele cria ou atualiza dados canônicos sem duplicação e sem criar usuários administrativos ou credenciais.

## Conteúdo inicial

- LABTEC.IN como unidade raiz e LATEC como filha.
- 33 pessoas e 43 memberships institucionais.
- Sete eixos da LATEC e nove mentorias.
- Projetos de portfólio práticos, equipes e resultados.
- A pesquisa formal “Pesquisa de Bioativos da Amazônia” publicada.
- Duas notícias e dois cursos, além dos materiais iniciais.
- Seis métricas vinculadas ao LABTEC.IN.
- Configuração do site, hero e seções institucionais.

O seed não cria papéis públicos globais, categorias ou tags de notícia, trilhas, eventos, MediaAssets nem a métrica `eventos`.

Unidades são criadas sem flags de ativação ou visibilidade, pois todo registro de `InstitutionalUnit` é público. Materiais também não recebem configuração de privacidade: sua exposição acompanha a publicação do curso.

## Classificação institucional

| Dado | Unidade inicial |
| --- | --- |
| Configuração, hero, seções e métricas | LABTEC.IN |
| Sete eixos e mentorias | LATEC |
| Ligantes | membership na LATEC |
| Pesquisadores e professores | membership no LABTEC.IN |
| Coordenação | memberships no LABTEC.IN e na LATEC |
| Notícias e cursos da Liga | LATEC |
| Pesquisa de Bioativos | LATEC |
| Produção científica e transparência gerais | LABTEC.IN |

Conteúdos semeados para a LATEC usam `include_in_parent_ecosystem=False`. Sua inclusão no recorte do LABTEC.IN depende de decisão editorial posterior.

## Memberships

Os 43 vínculos incluem:

- ligantes na LATEC;
- professores, pesquisadores e estagiários aplicáveis no LABTEC.IN;
- coordenação no LABTEC.IN e na LATEC;
- nove memberships `Mentor` na LATEC.

A chave estável é `(person, unit, role)`, portanto a mesma pessoa pode possuir `Coordenadora` e `Mentor` na LATEC.

## Pesquisa de Bioativos

`pesquisa-de-bioativos-da-amazonia` é semeada como `ResearchProject` publicada, mesmo sem arquivo. Em banco atualizado, o projeto de portfólio que serviu de origem permanece arquivado e não é republicado pelo seed. Em banco novo, a pesquisa não volta a ser criada como projeto de portfólio.

O comando não infere metodologia, instituição, datas ou autoria que não estejam nos dados canônicos.

## Idempotência

- Usar `slug`, `key` ou combinação única como chave estável.
- Criar unidades antes de memberships e conteúdos.
- Criar pessoas antes de equipes, contribuições e autorias.
- Criar eixos antes de mentorias.
- Não apagar registros editoriais criados manualmente.
- Não elevar novamente um registro que a coordenação arquivou depois do seed.

Dois ciclos consecutivos devem manter as mesmas 43 memberships, nove mentorias e seis métricas.

## Textos e identificadores atuais

- O hero descreve o LABTEC.IN como laboratório.
- Conteúdos da Liga usam “LATEC”.
- A biografia da coordenação distingue LABTEC.IN e LATEC.
- O seed localiza a configuração diretamente pela unidade LABTEC.IN e não aceita nomes institucionais legados como fallback.
- Os slugs atuais das notícias usam `latec`, não `latecin`. As duas URLs antigas não são recriadas nem recebem redirecionamento.
- Demais slugs explícitos permanecem estáveis quando apenas o título visível é corrigido.

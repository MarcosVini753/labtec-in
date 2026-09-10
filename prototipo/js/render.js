/*
  render.js
  Monta o HTML de cada rota do protótipo usando os dados de data.js.
*/

function escapeHTML(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function setActiveLink(route) {
  const links = document.querySelectorAll('.main-nav a');
  links.forEach(link => {
    link.classList.toggle('active', link.getAttribute('href') === route);
  });
}

function renderTags(tags) {
  return `
    <div class="tags">
      ${tags.filter(Boolean).map(tag => `<span class="tag">${escapeHTML(tag)}</span>`).join('')}
    </div>
  `;
}

function renderHome() {
  setActiveLink('#home');
  const main = document.getElementById('app');
  const latestNews = news.slice(0, 2);
  const featuredProjects = projects.slice(0, 2);

  main.innerHTML = `
    <section class="hero">
      <div class="container hero-grid">
        <div>
          <p class="section-kicker">Biotecnologia, biodiversidade e inovação</p>
          <h1>LATEC<span class="brand-line">.IN</span></h1>
          <p>Uma liga acadêmica conectando ensino, pesquisa e extensão para transformar ciência em soluções para a Amazônia.</p>
          <div class="hero-actions">
            <a href="#portfolio" class="btn btn-primary">Conheça os projetos</a>
            <a href="#contato" class="btn btn-secondary">Fale com a liga</a>
          </div>
        </div>
        <aside class="hero-panel" aria-label="Destaques da LATEC.IN">
          <ul>
            <li><strong>${impactNumbers.projetos}+</strong><span>projetos e iniciativas acadêmicas</span></li>
            <li><strong>${impactNumbers.membros}+</strong><span>membros em formação científica</span></li>
            <li><strong>${impactNumbers.parcerias}+</strong><span>parcerias para inovação aplicada</span></li>
          </ul>
        </aside>
      </div>
    </section>

    <section class="page-section">
      <div class="container">
        <div class="section-heading">
          <p class="section-kicker">Atualizações</p>
          <h2 class="section-title">Últimas notícias</h2>
        </div>
        <div class="card-grid">
          ${renderNewsCards(latestNews)}
        </div>
      </div>
    </section>

    <section class="page-section compact">
      <div class="container">
        <div class="section-heading">
          <p class="section-kicker">Portfólio</p>
          <h2 class="section-title">Projetos em destaque</h2>
        </div>
        <div class="card-grid">
          ${renderProjectCards(featuredProjects)}
        </div>
      </div>
    </section>

    <section class="page-section">
      <div class="container">
        <div class="section-heading">
          <p class="section-kicker">Nosso Impacto</p>
          <h2 class="section-title">Indicadores da LATEC.IN</h2>
          <p class="section-lead">Números simulados do protótipo para representar atividade acadêmica, produção e cooperação.</p>
        </div>
        <div class="impact-grid">
          <div class="impact-item"><span class="number">${impactNumbers.membros}</span><span class="label">Membros</span></div>
          <div class="impact-item"><span class="number">${impactNumbers.projetos}</span><span class="label">Projetos</span></div>
          <div class="impact-item"><span class="number">${impactNumbers.artigos}</span><span class="label">Artigos</span></div>
          <div class="impact-item"><span class="number">${impactNumbers.parcerias}</span><span class="label">Parcerias</span></div>
        </div>
      </div>
    </section>
  `;
}

function renderQuemSomos() {
  setActiveLink('#quem-somos');
  const main = document.getElementById('app');
  main.innerHTML = `
    <section class="page-section">
      <div class="container">
        <div class="section-heading">
          <p class="section-kicker">Institucional</p>
          <h2 class="section-title">Quem Somos</h2>
          <p class="section-lead">Pesquisa, ensino e extensão com foco em tecnologia, biodiversidade e inovação amazônica.</p>
        </div>
        <div class="content-panel prose">
          <p>A LATEC.IN (Liga Acadêmica de Biotecnologia, Biodiversidade e Inovação) é um núcleo de pesquisa, ensino e extensão da Universidade Federal do Acre. Nossa missão é desenvolver soluções tecnológicas e científicas para a Amazônia, promovendo a formação de profissionais capacitados e conscientes do papel da ciência na sociedade.</p>
          <p><strong>Visão:</strong> tornar-se referência nacional em inovação biotecnológica e proteção da biodiversidade amazônica.</p>
          <p><strong>Valores:</strong> ética, inovação, sustentabilidade, colaboração e excelência.</p>
        </div>
      </div>
    </section>
    <section class="page-section compact">
      <div class="container split-grid">
        <div class="content-panel">
          <h3>Linhas de Atuação</h3>
          <ul>
            <li>Inteligência Artificial aplicada à Biotecnologia</li>
            <li>Bootcamp de Startups</li>
            <li>Biodiversidade no setor acadêmico</li>
            <li>Farmacologia e biotecnologia para pesquisas científicas</li>
          </ul>
        </div>
        <div class="content-panel">
          <h3>Como Atuamos</h3>
          <p>Organizamos capacitações, projetos de pesquisa, ações de extensão e protótipos que aproximam estudantes, docentes e parceiros externos.</p>
        </div>
      </div>
    </section>
    <section class="page-section compact">
      <div class="container">
        <div class="section-heading">
          <h2 class="section-title">Nossa Equipe</h2>
        </div>
        <div class="card-grid">
          ${members.map(m => `
            <article class="card">
              <img class="card-media" src="${escapeHTML(m.foto)}" alt="Foto de ${escapeHTML(m.nome)}">
              <h3>${escapeHTML(m.nome)}</h3>
              ${renderTags([m.funcao])}
              <p>${escapeHTML(m.bio)}</p>
            </article>
          `).join('')}
        </div>
      </div>
    </section>
  `;
}

function renderPortfolio() {
  setActiveLink('#portfolio');
  const main = document.getElementById('app');
  const categories = ['todos', ...new Set(projects.map(project => project.categoria).filter(Boolean))];

  main.innerHTML = `
    <section class="page-section">
      <div class="container">
        <div class="section-heading">
          <p class="section-kicker">Projetos</p>
          <h2 class="section-title">Portfólio</h2>
          <p class="section-lead">Filtre iniciativas por categoria e acesse os detalhes de cada projeto.</p>
        </div>
        <div class="filter-panel" aria-label="Filtros do portfólio">
          <div id="portfolio-filters" class="filter-chips">
            ${categories.map((category, index) => `
              <button class="filter-chip ${index === 0 ? 'active' : ''}" type="button" data-filter="${escapeHTML(category)}" aria-pressed="${index === 0 ? 'true' : 'false'}">
                ${category === 'todos' ? 'Todos' : escapeHTML(category)}
              </button>
            `).join('')}
          </div>
          <button id="clear-portfolio-filter" class="btn btn-ghost" type="button">Limpar filtros</button>
          <p id="portfolio-count" class="result-count">${projects.length} projeto${projects.length === 1 ? '' : 's'}</p>
        </div>
        <div id="portfolio-list" class="card-grid">
          ${renderProjectCards(projects)}
        </div>
      </div>
    </section>
  `;

  const list = document.getElementById('portfolio-list');
  const count = document.getElementById('portfolio-count');
  const filterButtons = document.querySelectorAll('#portfolio-filters button');

  function applyFilter(category) {
    const filtered = filtrarPorCategoria(category, projects);
    list.innerHTML = renderProjectCards(filtered);
    count.textContent = `${filtered.length} projeto${filtered.length === 1 ? '' : 's'}`;
    filterButtons.forEach(button => {
      const isActive = button.dataset.filter === category || (category === 'todos' && button.dataset.filter === 'todos');
      button.classList.toggle('active', isActive);
      button.setAttribute('aria-pressed', isActive ? 'true' : 'false');
    });
  }

  filterButtons.forEach(button => {
    button.addEventListener('click', () => applyFilter(button.dataset.filter));
  });

  document.getElementById('clear-portfolio-filter').addEventListener('click', () => applyFilter('todos'));
}

function renderProjectCards(list) {
  if (!list.length) {
    return '<div class="empty-state">Nenhum projeto encontrado para esse filtro.</div>';
  }

  return list.map(proj => `
    <article class="card">
      <h3>${escapeHTML(proj.titulo)}</h3>
      <p>${escapeHTML(proj.resumo)}</p>
      ${renderTags([proj.categoria, proj.area, proj.ano])}
      <div class="card-actions">
        <a href="#projeto?id=${proj.id}" class="btn btn-secondary">Detalhes</a>
      </div>
    </article>
  `).join('');
}

function renderProjectDetail(id) {
  setActiveLink(null);
  const proj = projects.find(p => p.id === id);
  const main = document.getElementById('app');
  if (!proj) {
    renderNotFound();
    return;
  }

  const equipeNomes = (proj.equipe || []).map(eid => {
    const m = members.find(mem => mem.id === eid);
    return m ? m.nome : 'Membro';
  });
  const equipeTexto = proj.equipeTexto ? proj.equipeTexto.split('\n').map(nome => nome.trim()).filter(Boolean) : [];
  const equipeLista = equipeNomes.length ? equipeNomes : equipeTexto;

  main.innerHTML = `
    <section class="page-section">
      <div class="container">
        <div class="detail-actions">
          <a href="#portfolio" class="btn btn-secondary">Voltar para Portfólio</a>
        </div>
        <article class="content-panel detail-panel prose">
          <p class="section-kicker">Projeto</p>
          <h2 class="section-title">${escapeHTML(proj.titulo)}</h2>
          ${renderTags([proj.categoria, proj.area, proj.status, proj.ano])}
          <h3>Resumo do Problema</h3>
          <p>${escapeHTML(proj.problema)}</p>
          <h3>Solução Proposta</h3>
          <p>${escapeHTML(proj.solucao)}</p>
          <h3>Resultados / Produtos</h3>
          ${(proj.resultados || []).length ? `<ul>${proj.resultados.map(r => `<li>${escapeHTML(r)}</li>`).join('')}</ul>` : '<p>Resultados ainda não cadastrados.</p>'}
          <h3>Equipe</h3>
          ${equipeLista.length ? `<ul>${equipeLista.map(nome => `<li>${escapeHTML(nome)}</li>`).join('')}</ul>` : '<p>Equipe ainda não cadastrada.</p>'}
          ${proj.link ? `<p><a href="${escapeHTML(proj.link)}" target="_blank" rel="noopener" class="btn btn-primary">Acessar repositório ou aplicação</a></p>` : ''}
        </article>
      </div>
    </section>
  `;
}

function renderCapacitacao() {
  setActiveLink('#capacitacao');
  const main = document.getElementById('app');
  main.innerHTML = `
    <section class="page-section">
      <div class="container">
        <div class="section-heading">
          <p class="section-kicker">Formação</p>
          <h2 class="section-title">Capacitação e Cursos</h2>
          <p class="section-lead">Trilhas de aprendizagem, workshops e bootcamps para ampliar conhecimentos técnicos e científicos.</p>
        </div>
        <div class="card-grid">
          ${courses.map(curso => `
            <article class="card">
              <h3>${escapeHTML(curso.titulo)}</h3>
              <p>${escapeHTML(curso.descricao)}</p>
              ${renderTags([`Data: ${formatDate(curso.data)}`, curso.status])}
              <div class="card-actions">
                ${curso.link ? `<a href="${escapeHTML(curso.link)}" class="btn btn-secondary">Inscrever-se</a>` : '<span class="tag">Inscrições em breve</span>'}
              </div>
            </article>
          `).join('')}
        </div>
      </div>
    </section>
    <section class="page-section compact">
      <div class="container content-panel">
        <h3>Materiais de apoio</h3>
        <ul>
          ${materials.map(mat => `<li><a href="${escapeHTML(mat.arquivo)}" target="_blank" rel="noopener">${escapeHTML(mat.titulo)}</a> - ${escapeHTML(mat.descricao)}</li>`).join('')}
        </ul>
      </div>
    </section>
  `;
}

function renderNoticias() {
  setActiveLink('#noticias');
  const main = document.getElementById('app');
  main.innerHTML = `
    <section class="page-section">
      <div class="container">
        <div class="section-heading">
          <p class="section-kicker">Comunicação</p>
          <h2 class="section-title">Notícias e Publicações</h2>
          <p class="section-lead">Acompanhe editais, eventos e publicações da LATEC.IN.</p>
        </div>
        <div class="card-grid">
          ${renderNewsCards(news)}
        </div>
      </div>
    </section>
  `;
}

function renderNewsCards(list) {
  if (!list.length) {
    return '<div class="empty-state">Nenhuma notícia cadastrada ainda.</div>';
  }

  return list.map(post => `
    <article class="card">
      ${post.imagem ? `<img class="card-media" src="${escapeHTML(post.imagem)}" alt="">` : ''}
      <h3>${escapeHTML(post.titulo)}</h3>
      ${renderTags([post.categoria || post.tag, formatDate(post.data)])}
      <p>${escapeHTML(post.resumo)}</p>
      <div class="card-actions">
        <a href="#noticia?id=${post.id}" class="btn btn-secondary">Leia mais</a>
      </div>
    </article>
  `).join('');
}

function renderNewsDetail(id) {
  setActiveLink(null);
  const post = news.find(n => n.id === id);
  const main = document.getElementById('app');
  if (!post) {
    renderNotFound();
    return;
  }

  main.innerHTML = `
    <section class="page-section">
      <div class="container">
        <div class="detail-actions">
          <a href="#noticias" class="btn btn-secondary">Voltar para Notícias</a>
        </div>
        <article class="content-panel detail-panel prose">
          <p class="section-kicker">${escapeHTML(post.categoria || post.tag || 'Notícia')} - ${formatDate(post.data)}</p>
          <h2 class="section-title">${escapeHTML(post.titulo)}</h2>
          ${post.imagem ? `<img src="${escapeHTML(post.imagem)}" alt="${escapeHTML(post.titulo)}">` : ''}
          <p>${escapeHTML(post.conteudo)}</p>
        </article>
      </div>
    </section>
  `;
}

function renderContato() {
  setActiveLink('#contato');
  const main = document.getElementById('app');
  main.innerHTML = `
    <section class="page-section">
      <div class="container form-shell">
        <div class="section-heading">
          <p class="section-kicker">Contato</p>
          <h2 class="section-title">Contato e Parcerias</h2>
          <p class="section-lead">Envie dúvidas, solicitações de imprensa, propostas de parceria ou mensagens sobre processo seletivo.</p>
        </div>
        <form class="form-card" id="contact-form">
          <div class="form-grid">
            <div class="form-field full">
              <label for="tipo">Motivo do contato <span class="required">*</span></label>
              <select id="tipo" name="tipo" required>
                <option value="">Selecione uma categoria</option>
                <option value="duvidas">Dúvidas</option>
                <option value="imprensa">Imprensa</option>
                <option value="parceria">Quero ser parceiro</option>
                <option value="processo-seletivo">Processo seletivo</option>
                <option value="outro">Outro</option>
              </select>
              <p class="help-text">Isso ajuda a direcionar sua mensagem para o fluxo correto.</p>
            </div>
            <div class="form-field">
              <label for="nome">Nome <span class="required">*</span></label>
              <input type="text" id="nome" name="nome" autocomplete="name" required>
            </div>
            <div class="form-field">
              <label for="email">E-mail <span class="required">*</span></label>
              <input type="email" id="email" name="email" autocomplete="email" required>
            </div>
            <div class="form-field full">
              <label for="mensagem">Mensagem <span class="required">*</span></label>
              <textarea id="mensagem" name="mensagem" rows="6" required></textarea>
              <p class="help-text">Inclua contexto, prazos e links úteis, se existirem.</p>
            </div>
          </div>
          <button type="submit" class="btn btn-primary">Enviar mensagem</button>
          <p id="contact-success" class="form-message success" role="status">Mensagem enviada com sucesso. Entraremos em contato em breve.</p>
        </form>
      </div>
    </section>
  `;

  const form = document.getElementById('contact-form');
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    form.reset();
    document.getElementById('contact-success').classList.add('is-visible');
  });
}

function renderAdmin() {
  if (typeof showAdminArea === 'function') {
    showAdminArea();
  }
}

function renderNotFound() {
  const main = document.getElementById('app');
  main.innerHTML = `
    <section class="page-section">
      <div class="container content-panel">
        <h2 class="section-title">Página não encontrada</h2>
        <p>A página solicitada não existe ou não foi encontrada.</p>
        <a href="#home" class="btn btn-secondary">Voltar para Home</a>
      </div>
    </section>
  `;
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  const parts = String(dateStr).split('-');
  if (parts.length === 3) {
    const [year, month, day] = parts;
    return `${day.padStart(2, '0')}/${month.padStart(2, '0')}/${year}`;
  }
  const date = new Date(dateStr);
  if (isNaN(date)) return dateStr;
  return date.toLocaleDateString('pt-BR');
}

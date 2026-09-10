/*
  admin.js
  Simula uma área administrativa com login básico, criação e remoção de
  conteúdos salvos em localStorage.
*/

let adminLoggedIn = false;
let activeAdminForm = 'news';

function loadStoredData() {
  const storedProjects = localStorage.getItem('latec-projects');
  const storedNews = localStorage.getItem('latec-news');

  if (storedProjects) {
    try {
      const projArr = JSON.parse(storedProjects);
      if (Array.isArray(projArr) && projArr.length) {
        projects.length = 0;
        projArr.forEach(p => projects.push(p));
      }
    } catch (e) {
      console.error('Erro ao carregar projetos do localStorage', e);
    }
  }

  if (storedNews) {
    try {
      const newsArr = JSON.parse(storedNews);
      if (Array.isArray(newsArr) && newsArr.length) {
        news.length = 0;
        newsArr.forEach(n => news.push(n));
      }
    } catch (e) {
      console.error('Erro ao carregar notícias do localStorage', e);
    }
  }
}

function persistData() {
  localStorage.setItem('latec-projects', JSON.stringify(projects));
  localStorage.setItem('latec-news', JSON.stringify(news));
}

function fieldTemplate({ id, label, type = 'text', required = true, help = '', options = [], textarea = false, full = false, rows = 4 }) {
  const requiredMark = required ? '<span class="required">*</span>' : '';
  const requiredAttr = required ? 'required' : '';
  const helpText = help ? `<p class="help-text">${escapeHTML(help)}</p>` : '';

  if (options.length) {
    return `
      <div class="form-field ${full ? 'full' : ''}">
        <label for="${id}">${escapeHTML(label)} ${requiredMark}</label>
        <select id="${id}" ${requiredAttr}>
          <option value="">Selecione</option>
          ${options.map(option => `<option value="${escapeHTML(option)}">${escapeHTML(option)}</option>`).join('')}
        </select>
        ${helpText}
      </div>
    `;
  }

  if (textarea) {
    return `
      <div class="form-field ${full ? 'full' : ''}">
        <label for="${id}">${escapeHTML(label)} ${requiredMark}</label>
        <textarea id="${id}" rows="${rows}" ${requiredAttr}></textarea>
        ${helpText}
      </div>
    `;
  }

  return `
    <div class="form-field ${full ? 'full' : ''}">
      <label for="${id}">${escapeHTML(label)} ${requiredMark}</label>
      <input type="${type}" id="${id}" ${requiredAttr}>
      ${helpText}
    </div>
  `;
}

function renderAdminLogin(main) {
  main.innerHTML = `
    <section class="page-section">
      <div class="container admin-area">
        <div class="section-heading">
          <p class="section-kicker">Admin simulado</p>
          <h2 class="section-title">Área Administrativa</h2>
          <p class="section-lead">Acesse o painel para cadastrar notícias e projetos no protótipo local.</p>
        </div>
        <form id="login-form" class="form-card">
          <div class="form-grid">
            ${fieldTemplate({ id: 'login-email', label: 'E-mail', type: 'email', help: 'Use admin@latec.in para testar.' })}
            ${fieldTemplate({ id: 'login-senha', label: 'Senha', type: 'password', help: 'Use senha para testar.' })}
          </div>
          <button type="submit" class="btn btn-primary">Entrar</button>
          <p id="login-error" class="form-message error" role="alert">Credenciais inválidas. Tente novamente.</p>
        </form>
      </div>
    </section>
  `;

  document.getElementById('login-form').addEventListener('submit', function (e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value.trim();
    const senha = document.getElementById('login-senha').value;

    if (email === 'admin@latec.in' && senha === 'senha') {
      adminLoggedIn = true;
      localStorage.setItem('latec-admin', 'true');
      loadStoredData();
      renderAdmin();
      return;
    }

    document.getElementById('login-error').classList.add('is-visible');
  });
}

function renderNewsForm() {
  return `
    <form id="add-news-form" class="form-card" ${activeAdminForm === 'news' ? '' : 'hidden'}>
      <div class="form-grid">
        ${fieldTemplate({ id: 'news-titulo', label: 'Título', full: true })}
        ${fieldTemplate({ id: 'news-categoria', label: 'Categoria/tag', options: ['Edital', 'Evento', 'Pesquisa', 'Parceria', 'Publicação'] })}
        ${fieldTemplate({ id: 'news-data', label: 'Data', type: 'date' })}
        ${fieldTemplate({ id: 'news-resumo', label: 'Resumo', textarea: true, rows: 3, full: true, help: 'Texto curto para aparecer nos cards de notícia.' })}
        ${fieldTemplate({ id: 'news-conteudo', label: 'Conteúdo', textarea: true, rows: 6, full: true })}
        ${fieldTemplate({ id: 'news-imagem', label: 'URL da imagem', type: 'url', required: false, full: true, help: 'Campo opcional. Use uma imagem externa ou deixe em branco.' })}
        ${fieldTemplate({ id: 'news-status', label: 'Status', options: ['Publicado', 'Rascunho'] })}
      </div>
      <button type="submit" class="btn btn-primary">Salvar notícia</button>
    </form>
  `;
}

function renderProjectForm() {
  return `
    <form id="add-project-form" class="form-card" ${activeAdminForm === 'project' ? '' : 'hidden'}>
      <div class="form-grid">
        ${fieldTemplate({ id: 'project-titulo', label: 'Nome do projeto', full: true })}
        ${fieldTemplate({ id: 'project-categoria', label: 'Categoria', options: ['Ensino', 'Pesquisa', 'Extensão', 'Produção Científica', 'Startup', 'Premiação'] })}
        ${fieldTemplate({ id: 'project-area', label: 'Área', options: ['Biotecnologia', 'Biodiversidade', 'Inovação', 'Tecnologia', 'Educação', 'Comunidade'] })}
        ${fieldTemplate({ id: 'project-status', label: 'Status', options: ['Em andamento', 'Concluído', 'Planejado'] })}
        ${fieldTemplate({ id: 'project-ano', label: 'Ano', type: 'number' })}
        ${fieldTemplate({ id: 'project-link', label: 'Link externo ou repositório', type: 'url', required: false })}
        ${fieldTemplate({ id: 'project-resumo', label: 'Resumo', textarea: true, rows: 3, full: true })}
        ${fieldTemplate({ id: 'project-problema', label: 'Problema', textarea: true, rows: 3, full: true })}
        ${fieldTemplate({ id: 'project-solucao', label: 'Solução', textarea: true, rows: 3, full: true })}
        ${fieldTemplate({ id: 'project-resultados', label: 'Entregas/produtos', textarea: true, rows: 3, required: false, full: true, help: 'Separe cada entrega em uma linha.' })}
        ${fieldTemplate({ id: 'project-equipe', label: 'Equipe', textarea: true, rows: 2, required: false, full: true, help: 'Campo descritivo opcional para o protótipo.' })}
      </div>
      <button type="submit" class="btn btn-primary">Salvar projeto</button>
    </form>
  `;
}

function renderPreviewList(type) {
  const isNews = type === 'news';
  const items = isNews ? news.slice(0, 5) : projects.slice(0, 5);
  const emptyText = isNews ? 'Nenhuma notícia cadastrada ainda.' : 'Nenhum projeto cadastrado ainda.';

  if (!items.length) {
    return `<div class="empty-state">${emptyText}</div>`;
  }

  return `
    <div class="preview-list">
      ${items.map(item => `
        <div class="preview-item">
          <div>
            <strong>${escapeHTML(item.titulo)}</strong>
            <span>${escapeHTML(isNews ? `${formatDate(item.data)} - ${item.status || 'Publicado'}` : `${item.categoria} - ${item.status} - ${item.ano}`)}</span>
          </div>
          <button class="btn btn-danger" type="button" data-remove-type="${type}" data-remove-id="${item.id}">Remover</button>
        </div>
      `).join('')}
    </div>
  `;
}

function renderAdminPanel(main, feedback = '') {
  main.innerHTML = `
    <section class="page-section">
      <div class="container admin-area">
        <div class="admin-topbar">
          <div>
            <p class="section-kicker">Admin simulado</p>
            <h2 class="section-title">Cadastrar conteúdo</h2>
            <p class="section-lead">As alterações ficam salvas no navegador via localStorage.</p>
          </div>
          <button id="logout-btn" class="btn btn-secondary" type="button">Sair</button>
        </div>

        <div class="segmented-control" role="tablist" aria-label="Tipo de conteúdo">
          <button type="button" class="${activeAdminForm === 'news' ? 'active' : ''}" data-admin-tab="news" aria-selected="${activeAdminForm === 'news'}">Cadastrar Notícia</button>
          <button type="button" class="${activeAdminForm === 'project' ? 'active' : ''}" data-admin-tab="project" aria-selected="${activeAdminForm === 'project'}">Cadastrar Projeto</button>
        </div>

        <p id="admin-feedback" class="form-message success ${feedback ? 'is-visible' : ''}" role="status">${escapeHTML(feedback)}</p>

        <div class="admin-preview">
          ${renderNewsForm()}
          ${renderProjectForm()}
        </div>

        <div class="admin-preview">
          <h3>${activeAdminForm === 'news' ? 'Notícias recentes' : 'Projetos recentes'}</h3>
          ${renderPreviewList(activeAdminForm)}
        </div>
      </div>
    </section>
  `;

  bindAdminEvents();
}

function bindAdminEvents() {
  document.getElementById('logout-btn').addEventListener('click', () => {
    adminLoggedIn = false;
    localStorage.removeItem('latec-admin');
    renderAdmin();
  });

  document.querySelectorAll('[data-admin-tab]').forEach(button => {
    button.addEventListener('click', () => {
      activeAdminForm = button.dataset.adminTab;
      renderAdmin();
    });
  });

  document.getElementById('add-news-form').addEventListener('submit', function (e) {
    e.preventDefault();
    const newId = news.length ? Math.max(...news.map(n => Number(n.id) || 0)) + 1 : 1;
    news.unshift({
      id: newId,
      titulo: document.getElementById('news-titulo').value.trim(),
      categoria: document.getElementById('news-categoria').value,
      data: document.getElementById('news-data').value,
      resumo: document.getElementById('news-resumo').value.trim(),
      conteudo: document.getElementById('news-conteudo').value.trim(),
      imagem: document.getElementById('news-imagem').value.trim(),
      status: document.getElementById('news-status').value
    });
    persistData();
    activeAdminForm = 'news';
    renderAdminPanel(document.getElementById('app'), 'Notícia salva com sucesso.');
  });

  document.getElementById('add-project-form').addEventListener('submit', function (e) {
    e.preventDefault();
    const resultados = document.getElementById('project-resultados').value
      .split('\n')
      .map(item => item.trim())
      .filter(Boolean);
    const newId = projects.length ? Math.max(...projects.map(p => Number(p.id) || 0)) + 1 : 1;

    projects.unshift({
      id: newId,
      titulo: document.getElementById('project-titulo').value.trim(),
      categoria: document.getElementById('project-categoria').value,
      area: document.getElementById('project-area').value,
      status: document.getElementById('project-status').value,
      ano: parseInt(document.getElementById('project-ano').value, 10),
      resumo: document.getElementById('project-resumo').value.trim(),
      problema: document.getElementById('project-problema').value.trim(),
      solucao: document.getElementById('project-solucao').value.trim(),
      resultados,
      equipe: [],
      equipeTexto: document.getElementById('project-equipe').value.trim(),
      link: document.getElementById('project-link').value.trim()
    });
    persistData();
    activeAdminForm = 'project';
    renderAdminPanel(document.getElementById('app'), 'Projeto salvo com sucesso.');
  });

  document.querySelectorAll('[data-remove-type]').forEach(button => {
    button.addEventListener('click', () => {
      const id = Number(button.dataset.removeId);
      const collection = button.dataset.removeType === 'news' ? news : projects;
      const index = collection.findIndex(item => Number(item.id) === id);
      if (index >= 0) {
        collection.splice(index, 1);
        persistData();
        renderAdminPanel(document.getElementById('app'), 'Item removido com sucesso.');
      }
    });
  });
}

function showAdminArea() {
  setActiveLink('#admin');
  const main = document.getElementById('app');

  if (localStorage.getItem('latec-admin') === 'true') {
    adminLoggedIn = true;
  }

  if (!adminLoggedIn) {
    renderAdminLogin(main);
    return;
  }

  renderAdminPanel(main);
}

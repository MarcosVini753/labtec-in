import { escapeHTML, setActiveLink } from '../components/ui.mjs';
import { fetchPeopleList } from '../core/api.js';

export function renderLaboratorio() {
  setActiveLink('#laboratorio');
  const main = document.getElementById('app');

  main.innerHTML =
    '<section class="lab-hero">' +
      '<div class="container">' +
        '<p class="section-kicker">Laboratório LATEC.IN</p>' +
        '<h1>Laboratório de Biotecnologia, Biodiversidade e Inovação</h1>' +
        '<p class="section-lead">Infraestrutura, pesquisa aplicada e parcerias para transformar a ciência amazônica em solução real.</p>' +
      '</div>' +
    '</section>' +

    '<section class="page-section">' +
      '<div class="container">' +
        '<div class="section-heading">' +
            '<h2 class="section-title">O que é o Laboratório LATEC.IN</h2>' +
        '</div>' +
        '<div class="content-panel prose split-grid">' +
          '<p>O Laboratório LATEC.IN é o núcleo de execução prática da liga: junta experimentos, prototipação, instrumentação científica e orientação para ampliar a capacidade de geração de conhecimento da UFAC.</p>' +
          '<p>Diferente das ações extensionistas, o laboratório organiza a pesquisa continuous, cuida de equipamentos, protocolos e rotinas científicas para dar suporte a alunos, docentes e parceiros.</p>' +
        '</div>' +
      '</div>' +
    '</section>' +

    '<section class="page-section compact">' +
      '<div class="container">' +
        '<div class="section-heading">' +
          '<h2 class="section-title">Pilares do laboratório</h2>' +
        '</div>' +
        '<div class="lab-pillars">' +
          buildPillar('Infraestrutura', 'Equipamentos, salas limpas, bancadas e instrumentação científica disponível para projetos e ensaios.') +
          buildPillar('Pesquisa aplicada', 'Protocolos experimentais, mentorias científicas e apoio à execução de projetos de curso/IC.') +
          buildPillar('Dados e inovação', 'Modelagem, automação de rotinas, visualização de resultados e transferência de conhecimento para parceiros.') +
        '</div>' +
      '</div>' +
    '</section>' +

    '<section class="page-section compact">' +
      '<div class="container">' +
        '<div class="section-heading">' +
          '<h2 class="section-title">Pessoas do laboratório</h2>' +
          '<p class="section-lead">Filtre por ligantes ou por professores/mentores.</p>' +
        '</div>' +
        buildPeopleFilter('lab-people-filters', [
          { key: 'all', label: 'Todos' },
          { key: 'ligantes', label: 'Ligantes' },
          { key: 'mentores', label: 'Professores/Mentores' },
        ]) +
        '<div id="lab-people" class="card-grid"><div class="empty-state">Carregando equipe...</div></div>' +
      '</div>' +
    '</section>' +

    '<section class="page-section compact">' +
      '<div class="container">' +
        '<div class="section-heading">' +
          '<h2 class="section-title">Notícias do laboratório</h2>' +
          '<p class="section-lead">Experimentos, entrada de equipamentos, resultados e parcerias.</p>' +
        '</div>' +
        '<div id="lab-news" class="card-grid"><div class="empty-state">Carregando notícias...</div></div>' +
      '</div>' +
    '</section>' +

    '<section class="page-section compact">' +
      '<div class="container">' +
        '<div class="section-heading">' +
          '<h2 class="section-title">Projetos em andamento</h2>' +
          '<p class="section-lead">Ensaios, protótipos e iniciativas apoiadas pelo laboratório.</p>' +
        '</div>' +
        '<div id="lab-projects" class="card-grid"><div class="empty-state">Carregando projetos...</div></div>' +
      '</div>' +
    '</section>';

  let labPeople = [];
  fetchPeopleList()
    .then(function (payload) {
      labPeople = Array.isArray(payload) ? payload : (payload.results || []);
      applyLabPeopleFilter('all');
    })
    .catch(function () {
      const grid = document.getElementById('lab-people');
      if (grid) grid.innerHTML = '<div class="empty-state">Não foi possível carregar a equipe.</div>';
    });

  const filterContainer = document.getElementById('lab-people-filters');
  if (filterContainer) {
    filterContainer.addEventListener('click', function (event) {
      const button = event.target.closest('button[data-lab-filter]');
      if (!button) return;
      const key = button.getAttribute('data-lab-filter');
      applyLabPeopleFilter(key);
    });
  }

  function applyLabPeopleFilter(key) {
    const peopleGrid = document.getElementById('lab-people');
    if (!peopleGrid) return;

    const activeButtons = filterContainer.querySelectorAll('button[data-lab-filter]');
    activeButtons.forEach(function (btn) {
      const pressed = btn.getAttribute('data-lab-filter') === key;
      btn.setAttribute('aria-pressed', pressed ? 'true' : 'false');
      btn.classList.toggle('active', pressed);
    });

    const items = labPeople.map(function (p) {
      return {
        full_name: p.full_name || p.name || 'Membro',
        photo: p.photo || p.avatar || p.foto || '',
        short_bio: p.short_bio || p.bio || '',
        memberships: Array.isArray(p.memberships) ? p.memberships : Array.isArray(p.institution_memberships) ? p.institution_memberships : [],
      };
    });

    const filtered = items.filter(function (p) {
      if (key === 'all') return true;
      const matches = p.memberships.some(function (m) {
        const role = String(m.role || '').toLowerCase();
        const label = String(m.role_label || m.label || m.name || '').toLowerCase();
        if (key === 'ligantes') return /ligante|bolsista|estudante|aluno/.test(role) || /ligante|bolsista|estudante|aluno/.test(label);
        if (key === 'mentores') return /professor|mentor|docente|técnico|pesquisador/.test(role) || /professor|mentor|docente|técnico|pesquisador/.test(label);
        return false;
      });
      return matches;
    });

    if (!filtered.length) {
      peopleGrid.innerHTML = '<div class="empty-state">Nenhuma pessoa encontrada para esse filtro.</div>';
      return;
    }

    const cards = filtered.map(function (p) {
      const name = escapeHTML(p.full_name);
      const localPhoto = fallbackPhoto(p.full_name);
      const imageBlock = localPhoto
        ? '<div class="card-media-wrap"><img class="card-media" src="' + localPhoto + '" alt="Foto de ' + name + '"></div>'
        : '<div class="card-media-wrap"><div class="card-media-placeholder">SEM FOTO</div></div>';
      const bio = escapeHTML((p.short_bio || '').replace(/<[^>]+>/g, ''));
      return (
        '<article class="card">' +
          imageBlock +
          '<div class="card-body">' +
            '<h3>' + name + '</h3>' +
            '<p class="person-bio">' + (bio || '') + '</p>' +
          '</div>' +
        '</article>'
      );
    }).join('');

    peopleGrid.innerHTML = '<div class="card-grid">' + cards + '</div>';
  }
}

function buildPillar(title, text) {
  return (
    '<article class="card pillar-card">' +
      '<h3>' + escapeHTML(title) + '</h3>' +
      '<p>' + escapeHTML(text) + '</p>' +
    '</article>'
  );
}

function fallbackPhoto(fullName) {
  if (!fullName) return '';
  const base = String(fullName).trim().split(/\s+/)[0];
  const slug = base
    .toLowerCase()
    .replace(/[àáâãä]/g, 'a')
    .replace(/[èéêë]/g, 'e')
    .replace(/[ìíîï]/g, 'i')
    .replace(/[òóôõö]/g, 'o')
    .replace(/[ùúûü]/g, 'u')
    .replace(/[ñ]/g, 'n')
    .replace(/[ç]/g, 'c')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
  if (!slug) return '';
  return 'js/pics/' + slug + '.png';
}

export function buildPeopleFilter(containerId, filters) {
  const buttons = filters
    .map(function (f) {
      return (
        '<button class="filter-chip" type="button" data-lab-filter="' + escapeHTML(f.key) + '" aria-pressed="false">' +
          escapeHTML(f.label) +
        '</button>'
      );
    })
    .join('');
  return '<div id="' + containerId + '" class="filter-panel" aria-label="Filtros de pessoas">' + buttons + '</div>';
}

import { escapeHTML, setActiveLink } from '../components/ui.mjs';
import { fetchPeopleList } from '../core/api.js';

function personLabel(person) {
  const raw = person.role || (person.memberships || []).slice(0, 1).map(function (m) { return m.role; })[0] || '';
  return raw.trim();
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

function personCardHTML(p) {
  const label = personLabel(p);
  const category = String((label || '') + ' ' + (p.full_name || '')).toLowerCase();
  const isProfessor = label.toLowerCase().indexOf('professor') !== -1 || /dr\.?\b|doutor|doutora|dra\.?|engenheir/.test(label);
  const isLigant = category.indexOf('ligante') !== -1;

  const name = escapeHTML(p.full_name || 'Membro');
  const localPhoto = fallbackPhoto(p.full_name);
  const imageBlock = localPhoto
    ? '<div class="card-media-wrap"><img class="card-media" src="' + localPhoto + '" alt="Foto de ' + name + '"></div>'
    : '<div class="card-media-wrap"><div class="card-media-placeholder">SEM FOTO</div></div>';
  const bio = escapeHTML((p.short_bio || '').replace(/<[^>]+>/g, ''));

  return (
    '<article class="person-card" data-role="' + escapeHTML(label) + '" data-is-professor="' + (isProfessor ? '1' : '0') + '" data-is-ligant="' + (isLigant ? '1' : '0') + '">' +
      imageBlock +
      '<div class="person-info">' +
        '<p class="person-name">' + name + '</p>' +
        (label ? '<p class="person-role">' + escapeHTML(label) + '</p>' : '') +
        (bio ? '<p class="person-bio">' + bio + '</p>' : '') +
      '</div>' +
    '</article>'
  );
}

function applyTeamFilter(code) {
  const container = document.getElementById('quem-somos-grid');
  if (!container) return;

  const items = Array.prototype.slice.call(container.querySelectorAll('.person-card'));
  items.forEach(function (card) {
    const isProfessor = card.getAttribute('data-is-professor') === '1';
    const isLigant = card.getAttribute('data-is-ligant') === '1';
    let visible = true;

    if (code === 'ligantes') {
      visible = isLigant;
    } else if (code === 'professores') {
      visible = isProfessor;
    }

    card.style.display = visible ? '' : 'none';
  });
}

export function renderQuemSomos() {
  setActiveLink('#quem-somos');
  const main = document.getElementById('app');

  main.innerHTML =
    '<section class="page-section">' +
      '<div class="container">' +
        '<div class="section-heading">' +
          '<p class="section-kicker">Institucional</p>' +
          '<h2 class="section-title">Quem Somos</h2>' +
          '<p class="section-lead">Pesquisa, ensino e extensão com foco em tecnologia, biodiversidade e inovação amazônica.</p>' +
        '</div>' +
        '<div class="content-panel prose">' +
          '<p>A LATEC.IN (Liga Acadêmica de Biotecnologia, Biodiversidade e Inovação) é um núcleo de pesquisa, ensino e extensão da Universidade Federal do Acre. Nossa missão é desenvolver soluções tecnológicas e científicas para a Amazônia, promovendo a formação de profissionais capacitados e conscientes do papel da ciência na sociedade.</p>' +
          '<p><strong>Visão:</strong> tornar-se referência nacional em inovação biotecnológica e proteção da biodiversidade amazônica.</p>' +
          '<p><strong>Valores:</strong> ética, inovação, sustentabilidade, colaboração e excelência.</p>' +
        '</div>' +
      '</div>' +
    '</section>' +
    '<section class="page-section compact">' +
      '<div class="container split-grid">' +
        '<div class="content-panel">' +
          '<h3>Linhas de Atuação</h3>' +
          '<ul>' +
            '<li>Inteligência Artificial aplicada à Biotecnologia</li>' +
            '<li>Bootcamp de Startups</li>' +
            '<li>Biodiversidade no setor acadêmico</li>' +
            '<li>Farmacologia e biotecnologia para pesquisas científicas</li>' +
          '</ul>' +
        '</div>' +
        '<div class="content-panel">' +
          '<h3>Como Atuamos</h3>' +
          '<p>Organizamos capacitações, projetos de pesquisa, ações de extensão e protótipos que aproximam estudantes, docentes e parceiros externos.</p>' +
        '</div>' +
      '</div>' +
    '</section>' +
    '<section class="page-section compact">' +
      '<div class="container">' +
        '<div class="section-heading">' +
          '<h2 class="section-title">Nossa Equipe</h2>' +
          '<div id="quem-somos-team" class="team-section">' +
            '<div class="team-filters" role="group" aria-label="Filtro da equipe">' +
              '<button class="filter-chip active" data-filter="all">Todos</button>' +
              '<button class="filter-chip" data-filter="ligantes">Ligantes</button>' +
              '<button class="filter-chip" data-filter="professores">Professores</button>' +
            '</div>' +
            '<div id="quem-somos-grid" class="team-grid">' +
              '<div class="empty-state">Carregando equipe...</div>' +
            '</div>' +
          '</div>' +
    '</section>';

  fetchPeopleList()
    .then(function (payload) {
      const items = Array.isArray(payload) ? payload : (payload.results || []);
      const grid = document.getElementById('quem-somos-grid');
      if (!grid) return;

      const cards = items.map(personCardHTML).join('');
      grid.innerHTML = cards || '<div class="empty-state">Nenhuma pessoa cadastrada.</div>';

      const first = document.querySelector('.team-filters .filter-chip');
      if (first) {
        applyTeamFilter(first.getAttribute('data-filter') || 'all');
      }

      Array.prototype.slice.call(document.querySelectorAll('.team-filters .filter-chip')).forEach(function (chip) {
        chip.addEventListener('click', function () {
          Array.prototype.slice.call(document.querySelectorAll('.team-filters .filter-chip')).forEach(function (btn) {
            btn.classList.remove('active');
          });
          chip.classList.add('active');
          applyTeamFilter(chip.getAttribute('data-filter') || 'all');
        });
      });
    })
    .catch(function () {
      const grid = document.getElementById('quem-somos-grid');
      if (grid) grid.innerHTML = '<div class="empty-state">Não foi possível carregar a equipe.</div>';
    });
}

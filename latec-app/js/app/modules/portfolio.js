import { escapeHTML, renderProjectCards, setActiveLink } from '../components/ui.mjs';
import { fetchProjects } from '../core/api.js';

export function renderPortfolio() {
  setActiveLink('#portfolio');
  const main = document.getElementById('app');
  main.innerHTML =
    '<section class="page-section">' +
      '<div class="container">' +
        '<div class="section-heading">' +
          '<p class="section-kicker">Projetos</p>' +
          '<h2 class="section-title">Portfólio</h2>' +
          '<p class="section-lead">Filtre iniciativas por categoria e busque por título.</p>' +
        '</div>' +
        '<div class="filter-panel" aria-label="Filtros do portfólio">' +
          '<div id="portfolio-filters" class="filter-chips">' +
            '<label class="sr-only" for="portfolio-search">Buscar projetos</label>' +
            '<input id="portfolio-search" type="search" placeholder="Buscar projetos..." autocomplete="off">' +
            '<div id="category-chips"></div>' +
          '</div>' +
          '<div class="filter-meta">' +
            '<button id="clear-portfolio-filter" class="btn btn-ghost" type="button">Limpar filtros</button>' +
            '<p id="portfolio-count" class="result-count"></p>' +
          '</div>' +
        '</div>' +
        '<div id="portfolio-list" class="card-grid">' +
          '<div class="empty-state">Carregando projetos...</div>' +
        '</div>' +
      '</div>' +
    '</section>';

  fetchProjects()
    .then(function (items) {
      renderPortfolioList(items);
    })
    .catch(function () {
      var list = document.getElementById('portfolio-list');
      if (list) list.innerHTML = '<div class="empty-state">Não foi possível carregar os projetos.</div>';
    });
}

export function renderProjectDetail(id) {
  setActiveLink(null);
  const main = document.getElementById('app');

  fetchProjects()
    .then(function (items) {
      const proj = items.find(function (p) { return p.id === id; });
      if (!proj) {
        renderNotFound();
        return;
      }

      const equipeNomes = Array.isArray(proj.team_members)
        ? proj.team_members.map(function (tm) {
            const p = tm.person || {};
            return p.full_name || p.name || 'Membro';
          })
        : [];

      main.innerHTML =
        '<section class="page-section">' +
          '<div class="container">' +
            '<div class="detail-actions">' +
              '<a href="#portfolio" class="btn btn-secondary">Voltar para Portfólio</a>' +
            '</div>' +
            '<article class="content-panel detail-panel prose">' +
              '<p class="section-kicker">Projeto</p>' +
              '<h2 class="section-title">' + escapeHTML(proj.title || proj.name || 'Projeto') + '</h2>' +
              renderTags([
                proj.category && proj.category.name ? proj.category.name : '',
                proj.area ? proj.area : '',
                proj.status && proj.status.name ? proj.status.name : '',
                String(proj.year || ''),
              ]) +
              '<h3>Resumo do Problema</h3>' +
              '<p>' + escapeHTML(proj.problem || proj.summary || '') + '</p>' +
              '<h3>Solução Proposta</h3>' +
              '<p>' + escapeHTML(proj.solution || '') + '</p>' +
              '<h3>Resultados / Produtos</h3>' +
              (Array.isArray(proj.results) && proj.results.length
                ? '<ul>' + proj.results.map(function (r) { return '<li>' + escapeHTML(r.title || r.description || '') + '</li>'; }).join('') + '</ul>'
                : '<p>Resultados ainda não cadastrados.</p>') +
              '<h3>Equipe</h3>' +
              (equipeNomes.length
                ? '<ul>' + equipeNomes.map(function (nome) { return '<li>' + escapeHTML(nome) + '</li>'; }).join('') + '</ul>'
                : '<p>Equipe ainda não cadastrada.</p>') +
              (proj.links && proj.links.length
                ? '<p>' + proj.links.map(function (l) { return '<a href="' + escapeHTML(l.url) + '" target="_blank" rel="noopener" class="btn btn-primary">' + escapeHTML(l.label || 'Acessar') + '</a>'; }).join(' ') + '</p>'
                : '') +
            '</article>' +
          '</div>' +
        '</section>';
    })
    .catch(function () {
      renderNotFound();
    });
}

function renderPortfolioList(projectsData) {
  const list = document.getElementById('portfolio-list');
  const count = document.getElementById('portfolio-count');
  const chips = document.querySelectorAll('#category-chips button');
  const search = document.getElementById('portfolio-search');
  const clear = document.getElementById('clear-portfolio-filter');

  if (!list) return;

  const categories = ['todos'].concat(
    Array.from(new Set(projectsData.map(function (p) { return p.category && p.category.name ? p.category.name : 'Sem categoria'; }).filter(Boolean)))
  );
  const chipsContainer = document.getElementById('category-chips');
  if (chipsContainer) {
    chipsContainer.innerHTML = categories
      .map(function (cat, index) {
        const active = index === 0 ? ' active' : '';
        const pressed = index === 0 ? 'true' : 'false';
        const label = cat === 'todos' ? 'Todos' : escapeHTML(cat);
        return '<button class="filter-chip' + active + '" type="button" data-filter="' + escapeHTML(cat) + '" aria-pressed="' + pressed + '">' + label + '</button>';
      })
      .join('');
  }

  if (count) count.textContent = projectsData.length + ' projeto' + (projectsData.length === 1 ? '' : 's');

  function apply(category, term) {
    term = (term || '').trim().toLowerCase();
    let filtered = projectsData;
    if (category && category !== 'todos') {
      filtered = filtered.filter(function (p) {
        const catName = p.category && p.category.name ? p.category.name : 'Sem categoria';
        return catName === category;
      });
    }
    if (term) {
      filtered = filtered.filter(function (p) {
        const text = (p.title || p.name || '') + ' ' + (p.summary || '');
        return text.toLowerCase().indexOf(term) !== -1;
      });
    }
    if (list) list.innerHTML = renderProjectCards(filtered);
    if (count) count.textContent = filtered.length + ' projeto' + (filtered.length === 1 ? '' : 's');
  }

  if (chipsContainer) {
    chipsContainer.querySelectorAll('button').forEach(function (btn) {
      btn.addEventListener('click', function () {
        chipsContainer.querySelectorAll('button').forEach(function (b) {
          b.classList.remove('active');
          b.setAttribute('aria-pressed', 'false');
        });
        btn.classList.add('active');
        btn.setAttribute('aria-pressed', 'true');
        apply(btn.getAttribute('data-filter'), search ? search.value : '');
      });
    });
  }

  if (search) {
    search.addEventListener('input', function () {
      const active = document.querySelector('#category-chips button.active');
      const cat = active ? active.getAttribute('data-filter') : 'todos';
      apply(cat, search.value);
    });
  }

  if (clear) {
    clear.addEventListener('click', function () {
      const first = document.querySelector('#category-chips button');
      if (first) {
        first.classList.add('active');
        first.setAttribute('aria-pressed', 'true');
      }
      if (search) search.value = '';
      apply('todos', '');
    });
  }
}

export function renderNotFound() {
  const main = document.getElementById('app');
  main.innerHTML =
    '<section class="page-section">' +
      '<div class="container content-panel">' +
        '<h2 class="section-title">Página não encontrada</h2>' +
        '<p>A página solicitada não existe ou não foi encontrada.</p>' +
        '<a href="#home" class="btn btn-secondary">Voltar para Home</a>' +
      '</div>' +
    '</section>';
}

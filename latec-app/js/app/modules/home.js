import { escapeHTML, renderNewsCards, renderProjectCards, setActiveLink } from '../components/ui.mjs';
import { fetchHome, fetchPeopleList } from '../core/api.js';

function resolveLocalPhoto(fullName) {
  const name = String(fullName || '').trim();
  if (!name) return '';
  const base = name.split(/\s+/)[0].toLowerCase().normalize('NFD').replace(/[àáâãä]/g, 'a').replace(/[èéêë]/g, 'e').replace(/[ìíîï]/g, 'i').replace(/[òóôõö]/g, 'o').replace(/[ùúûü]/g, 'u').replace(/[ñ]/g, 'n').replace(/[ç]/g, 'c').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
  if (!base) return '';
  return 'js/pics/' + base + '.png';
}

function startHomePeopleCarousel() {
  const root = document.querySelector('.home-people-carousel');
  if (!root) return;
  const items = root.querySelectorAll('.person-card');
  if (items.length <= 3) return;

  let index = 0;
  const go = function () {
    const target = index % items.length;
    items[target].scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
    index = (target + 1) % items.length;
  };
  root._homeCarouselTimer = setInterval(go, 2200);
  root.addEventListener('pointerenter', function () { clearInterval(root._homeCarouselTimer); });
  root.addEventListener('pointerleave', function () { root._homeCarouselTimer = setInterval(go, 2200); });
}

function personLabel(person) {
  const memberships = (person.memberships || []).slice(0, 1);
  return memberships.map(function (m) {
    const unitName = m && m.unit ? escapeHTML(m.unit.name) : '';
    const role = escapeHTML(m.role || '');
    return unitName && role ? unitName + ' — ' + role : (unitName || role);
  })[0] || '';
}

function renderPersonCards(list, targetSelector) {
  const target = document.querySelector(targetSelector);
  if (!target) return;
  if (!list.length) {
    target.innerHTML = '<div class="empty-state">Nenhuma pessoa cadastrada.</div>';
    return;
  }

  const cards = list.map(function (p) {
    const name = escapeHTML(p.full_name || 'Membro');
    const localPhoto = resolveLocalPhoto(p.full_name);
    const imageBlock = localPhoto
      ? '<div class="card-media-wrap"><img class="card-media" src="' + localPhoto + '" alt="Foto de ' + name + '"></div>'
      : '<div class="card-media-wrap"><div class="card-media-placeholder">SEM FOTO</div></div>';

    const label = personLabel(p);
    const bio = escapeHTML((p.short_bio || '').replace(/<[^>]+>/g, ''));

    return (
      '<article class="person-card">' +
        imageBlock +
        '<div class="person-info">' +
          '<p class="person-name">' + name + '</p>' +
          (label ? '<p class="person-role">' + label + '</p>' : '') +
          (bio ? '<p class="person-bio">' + bio + '</p>' : '') +
        '</div>' +
      '</article>'
    );
  }).join('');

  target.innerHTML = '<div class="home-people-carousel">' + cards + '</div>';
  if (!target.querySelector('.home-people-carousel')) {
    target.innerHTML = '<div class="card-grid">' + cards + '</div>';
  }
  startHomePeopleCarousel();
}

function buildPillar(title, text) {
  return '<article class="card pillar-card"><h3>' + escapeHTML(title) + '</h3><p>' + escapeHTML(text) + '</p></article>';
}

export function renderHome(route) {
  setActiveLink(route || '#home');
  const main = document.getElementById('app');

  const heroFallback = {
    settings: null,
    heroes: [],
    impact_metrics: [
      { key: 'infra', value: 'Infraestrutura', label: 'Salas limpas, bancadas e instrumentação' },
      { key: 'pesquisa', value: 'Pesquisa aplicada', label: 'Protocolos, mentorias e apoio a IC' },
      { key: 'dados', value: 'Dados e inovação', label: 'Modelagem, automação e visualização' },
    ],
  };

  Promise.all([fetchHome(), fetchPeopleList({withMemberships: true}).catch(() => [])])
    .then(function (results) {
      const data = results[0];
      const peoplePayload = results[1];
      const people = Array.isArray(peoplePayload) ? peoplePayload : ((peoplePayload && peoplePayload.results) || []);
      const impactMetrics = Array.isArray(data.impact_metrics) && data.impact_metrics.length
        ? data.impact_metrics.slice(0, 3)
        : heroFallback.impact_metrics;

      const latestNews = Array.isArray(data.posts) ? data.posts.slice(0, 2) : [];
      const featuredProjects = Array.isArray(data.projects) ? data.projects.slice(0, 2) : [];

      main.innerHTML =
        '<section class="hero">' +
          '<div class="container hero-grid">' +
            '<div>' +
              '<p class="section-kicker">Laboratório LATEC.IN</p>' +
              '<h1>Laboratório de Biotecnologia, Biodiversidade e Inovação</h1>' +
              '<p>' + escapeHTML(settings && settings.description ? settings.description : 'Infraestrutura, pesquisa aplicada e parcerias para transformar a ciência amazônica em solução real.') + '</p>' +
              '<div class="hero-actions">' +
                '<a href="#portfolio" class="btn btn-primary">Conheça os projetos</a>' +
                '<a href="#contato" class="btn btn-secondary">Fale com o laboratório</a>' +
              '</div>' +
            '</div>' +
            '<aside class="hero-panel" aria-label="Destaques do Laboratório">' +
              '<ul>' +
                impactMetrics.map(function (item) {
                  return '<li><strong>' + escapeHTML(String(item.value ?? '')) + '</strong><span>' + escapeHTML(item.label || item.key || '') + '</span></li>';
                }).join('') +
              '</ul>' +
            '</aside>' +
          '</div>' +
        '</section>' +

        '<section class="page-section compact">' +
          '<div class="container">' +
            '<div class="section-heading">' +
              '<h2 class="section-title">O que é o Laboratório LATEC.IN</h2>' +
              '<p class="section-lead">Núcleo de execução prática da LATEC.IN: experimentos, prototipação, instrumentação científica e mentoria para ampliar a capacidade de geração de conhecimento na UFAC.</p>' +
            '</div>' +
          '</div>' +
        '</section>' +

        '<section class="page-section compact">' +
          '<div class="container">' +
            '<div class="section-heading">' +
              '<h2 class="section-title">Pilares</h2>' +
            '</div>' +
            '<div class="card-grid">' +
              buildPillar('Infraestrutura', 'Equipamentos, salas limpas, bancadas e instrumentação científica para projetos e ensaios.') +
              buildPillar('Pesquisa aplicada', 'Protocolos experimentais, mentorias científicas e apoio à execução de projetos de curso e IC.') +
              buildPillar('Dados e inovação', 'Modelagem, automação de rotinas, visualização de resultados e transferência técnica para parceiros.') +
            '</div>' +
          '</div>' +
        '</section>' +

        '<section class="page-section">' +
          '<div class="container">' +
            '<div class="section-heading">' +
              '<p class="section-kicker">Atualizações</p>' +
              '<h2 class="section-title">Últimas notícias</h2>' +
            '</div>' +
            '<div class="card-grid">' +
              (latestNews.length ? renderNewsCards(latestNews) : '<div class="empty-state">Nenhuma notícia publicada.</div>') +
            '</div>' +
          '</div>' +
        '</section>' +

        '<section class="page-section compact">' +
          '<div class="container">' +
            '<div class="section-heading">' +
              '<p class="section-kicker">Portfólio</p>' +
              '<h2 class="section-title">Projetos em destaque</h2>' +
            '</div>' +
            '<div class="card-grid">' +
              (featuredProjects.length ? renderProjectCards(featuredProjects) : '<div class="empty-state">Nenhum projeto em destaque.</div>') +
            '</div>' +
          '</div>' +
        '</section>' +

        '<section class="page-section">' +
          '<div class="container">' +
            '<div class="section-heading">' +
              '<p class="section-kicker">Nosso Impacto</p>' +
              '<h2 class="section-title">Indicadores do Laboratório</h2>' +
              '<p class="section-lead">Números da nossa operação acadêmica, científica e de inovação.</p>' +
            '</div>' +
            '<div class="impact-grid">' +
              impactMetrics.map(function (item) {
                return '<div class="impact-item"><span class="number">' + escapeHTML(String(item.value ?? '')) + '</span><span class="label">' + escapeHTML(item.label || item.key || '') + '</span></div>';
              }).join('') +
            '</div>' +
          '</div>' +
        '</section>' +

        '<section class="page-section">' +
          '<div class="container">' +
            '<div class="section-heading">' +
              '<p class="section-kicker">Pessoas do laboratório</p>' +
              '<h2 class="section-title">Equipe</h2>' +
            '</div>' +
            '<div id="home-people-grid"></div>' +
          '</div>' +
        '</section>';
    })
    .catch(function () {
      main.innerHTML =
        '<section class="hero">' +
          '<div class="container hero-grid">' +
            '<div>' +
              '<p class="section-kicker">Laboratório LATEC.IN</p>' +
              '<h1>Laboratório de Biotecnologia, Biodiversidade e Inovação</h1>' +
              '<p>Infraestrutura, pesquisa aplicada e parcerias para transformar a ciência amazônica em solução real.</p>' +
              '<div class="hero-actions">' +
                '<a href="#portfolio" class="btn btn-primary">Conheça os projetos</a>' +
                '<a href="#contato" class="btn btn-secondary">Fale com o laboratório</a>' +
              '</div>' +
            '</div>' +
            '<aside class="hero-panel" aria-label="Destaques do Laboratório">' +
              '<ul>' +
                heroFallback.impact_metrics.map(function (item) {
                  return '<li><strong>' + escapeHTML(item.value || '') + '</strong><span>' + escapeHTML(item.label || item.key || '') + '</span></li>';
                }).join('') +
              '</ul>' +
            '</aside>' +
          '</div>' +
        '</section>' +

        '<section class="page-section compact">' +
          '<div class="container">' +
            '<div class="section-heading">' +
              '<h2 class="section-title">O que é o Laboratório LATEC.IN</h2>' +
              '<p class="section-lead">Núcleo de execução prática da LATEC.IN: experimentos, prototipação, instrumentação científica e mentoria para ampliar a capacidade de geração de conhecimento na UFAC.</p>' +
            '</div>' +
          '</div>' +
        '</section>' +

        '<section class="page-section compact">' +
          '<div class="container">' +
            '<div class="section-heading">' +
              '<h2 class="section-title">Pilares</h2>' +
            '</div>' +
            '<div class="card-grid">' +
              buildPillar('Infraestrutura', 'Equipamentos, salas limpas, bancadas e instrumentação científica para projetos e ensaios.') +
              buildPillar('Pesquisa aplicada', 'Protocolos experimentais, mentorias científicas e apoio à execução de projetos de curso e IC.') +
              buildPillar('Dados e inovação', 'Modelagem, automação de rotinas, visualização de resultados e transferência técnica para parceiros.') +
            '</div>' +
          '</div>' +
        '</section>' +

        '<section class="page-section">' +
          '<div class="container">' +
            '<div class="section-heading">' +
              '<p class="section-kicker">Atualizações</p>' +
              '<h2 class="section-title">Últimas notícias</h2>' +
            '</div>' +
            '<div class="card-grid"><div class="empty-state">Não foi possível carregar as notícias.</div></div>' +
          '</div>' +
        '</section>' +

        '<section class="page-section compact">' +
          '<div class="container">' +
            '<div class="section-heading">' +
              '<p class="section-kicker">Portfólio</p>' +
              '<h2 class="section-title">Projetos em destaque</h2>' +
            '</div>' +
            '<div class="card-grid"><div class="empty-state">Não foi possível carregar os projetos.</div></div>' +
          '</div>' +
        '</section>' +

        '<section class="page-section">' +
          '<div class="container">' +
            '<div class="section-heading">' +
              '<p class="section-kicker">Pessoas do laboratório</p>' +
              '<h2 class="section-title">Equipe</h2>' +
            '</div>' +
            '<div class="card-grid"><div class="empty-state">Não foi possível carregar a equipe.</div></div>' +
          '</div>' +
        '</section>';
    })
    .then(function () {
      renderPersonCards(people, '#home-people-grid');
    });
}

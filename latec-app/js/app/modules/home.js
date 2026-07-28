import { formatDate } from '../core/utils.js';
import { fetchHome } from '../core/api.js';
import { escapeHTML, renderNewsCards, renderProjectCards, setActiveLink } from '../components/ui.mjs';

export function renderHome() {
  setActiveLink('#home');
  const main = document.getElementById('app');

  const heroFallback = {
    settings: null,
    heroes: [],
    impact_metrics: [
      { title: 'Projetos', value: 20 },
      { title: 'Membros', value: 15 },
      { title: 'Parcerias', value: 5 },
    ],
  };

  fetchHome()
    .then(function (data) {
      const settings = data.settings || heroFallback.settings;
      const heroes = Array.isArray(data.heroes) ? data.heroes : heroFallback.heroes;
      const latestNews = Array.isArray(data.posts) ? data.posts.slice(0, 2) : [];
      const featuredProjects = Array.isArray(data.projects)
        ? data.projects.slice(0, 2)
        : [];
      const impactMetrics = Array.isArray(data.impact_metrics) && data.impact_metrics.length
        ? data.impact_metrics
        : heroFallback.impact_metrics;

      main.innerHTML =
        '<section class="hero">' +
          '<div class="container hero-grid">' +
            '<div>' +
              '<p class="section-kicker">Biotecnologia, biodiversidade e inovação</p>' +
              '<h1>LABTEC<span class="brand-line">.IN</span></h1>' +
              '<p>' + escapeHTML(settings && settings.description ? settings.description : 'Educação que transforma') + '</p>' +
              '<div class="hero-actions">' +
                '<a href="#portfolio" class="btn btn-primary">Conheça os projetos</a>' +
                '<a href="#contato" class="btn btn-secondary">Fale com a liga</a>' +
              '</div>' +
            '</div>' +
            '<aside class="hero-panel" aria-label="Destaques da LABTEC.IN">' +
              '<ul>' +
                impactMetrics.map(function (item) {
                  return (
                    '<li><strong>' + escapeHTML(String(item.value || item.title || '')) + '</strong><span>' + escapeHTML(item.title || '') + '</span></li>'
                  );
                }).join('') +
              '</ul>' +
            '</aside>' +
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
              '<h2 class="section-title">Indicadores da LABTEC.IN</h2>' +
              '<p class="section-lead">Números do nosso ecossistema acadêmico.</p>' +
            '</div>' +
            '<div class="impact-grid">' +
              (impactMetrics.length
                ? impactMetrics.map(function (item) {
                    return (
                      '<div class="impact-item"><span class="number">' + escapeHTML(String(item.value || 0)) + '</span><span class="label">' + escapeHTML(item.title || '') + '</span></div>'
                    );
                  }).join('')
                : '<div class="empty-state">Sem indicadores cadastrados.</div>') +
            '</div>' +
          '</div>' +
        '</section>';
    })
    .catch(function () {
      main.innerHTML =
        '<section class="hero">' +
          '<div class="container hero-grid">' +
            '<div>' +
              '<p class="section-kicker">Biotecnologia, biodiversidade e inovação</p>' +
              '<h1>LABTEC<span class="brand-line">.IN</span></h1>' +
              '<p>Educação que transforma</p>' +
              '<div class="hero-actions">' +
                '<a href="#portfolio" class="btn btn-primary">Conheça os projetos</a>' +
                '<a href="#contato" class="btn btn-secondary">Fale com a liga</a>' +
              '</div>' +
            '</div>' +
            '<aside class="hero-panel" aria-label="Destaques da LABTEC.IN">' +
              '<ul>' +
                '<li><strong>20+</strong><span>projetos e iniciativas acadêmicas</span></li>' +
                '<li><strong>15+</strong><span>membros em formação científica</span></li>' +
                '<li><strong>5+</strong><span>parcerias para inovação aplicada</span></li>' +
              '</ul>' +
            '</aside>' +
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
              '<p class="section-kicker">Nosso Impacto</p>' +
              '<h2 class="section-title">Indicadores da LABTEC.IN</h2>' +
              '<p class="section-lead">Números simulados do protótipo para representar atividade acadêmica, produção e cooperação.</p>' +
            '</div>' +
            '<div class="impact-grid">' +
              '<div class="impact-item"><span class="number">20</span><span class="label">Projetos</span></div>' +
              '<div class="impact-item"><span class="number">15</span><span class="label">Membros</span></div>' +
              '<div class="impact-item"><span class="number">12</span><span class="label">Artigos</span></div>' +
              '<div class="impact-item"><span class="number">5</span><span class="label">Parcerias</span></div>' +
            '</div>' +
          '</div>' +
        '</section>';
    });
}

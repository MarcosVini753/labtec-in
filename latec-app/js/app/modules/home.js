import { escapeHTML, renderNewsCards, renderProjectCards, setActiveLink } from '../components/ui.mjs';
import { fetchHome, fetchPeopleList } from '../core/api.js';

export function renderHome(route) {
  setActiveLink(route || '#home');
  const main = document.getElementById('app');

  const heroFallback = {
    settings: null,
    heroes: [],
    impact_metrics: [
      { title: 'Infraestrutura', value: 'Salas limpas, bancadas e instrumentação' },
      { title: 'Pesquisa aplicada', value: 'Protocolos, mentorias e apoio a IC' },
      { title: 'Dados e inovação', value: 'Modelagem, automação e visualização' },
    ],
  };

  Promise.all([
    fetchHome(),
    fetchPeopleList().catch(() => []),
  ])
    .then(function (results) {
      const data = results[0];
      const people = results[1];

      const settings = data.settings || heroFallback.settings;
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
                  return (
                    '<li><strong>' + escapeHTML(String(item.value || item.title || '')) + '</strong><span>' + escapeHTML(item.title || '') + '</span></li>'
                  );
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
              '<h2 class="section-title">Pessoas do laboratório</h2>' +
              '<p class="section-lead">Professores, técnicos, ligantes e pesquisadores que mantêm o lab funcionando.</p>' +
            '</div>' +
            '<div class="card-grid">' +
              (people.length ? people.slice(0, 6).map(function (person) {
                return (
                  '<article class="card">' +
                    '<h3>' + escapeHTML(person.full_name) + '</h3>' +
                    '<p class="section-lead">' + escapeHTML(person.slug || 'Membro do laboratório') + '</p>' +
                  '</article>'
                );
              }).join('') : '<div class="empty-state">Carregando equipe...</div>') +
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
                '<li><strong>Infraestrutura</strong><span>Salas limpas, bancadas e instrumentação</span></li>' +
                '<li><strong>Pesquisa aplicada</strong><span>Protocolos, mentorias e apoio a IC</span></li>' +
                '<li><strong>Dados e inovação</strong><span>Modelagem, automação e visualização</span></li>' +
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
              '<h2 class="section-title">Pessoas do laboratório</h2>' +
              '<p class="section-lead">Professores, técnicos, ligantes e pesquisadores que mantêm o lab funcionando.</p>' +
            '</div>' +
            '<div class="card-grid"><div class="empty-state">Não foi possível carregar a equipe.</div></div>' +
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
              '<h2 class="section-title">Indicadores do Laboratório</h2>' +
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

function buildPillar(title, text) {
  return (
    '<article class="card">' +
      '<h3>' + escapeHTML(title) + '</h3>' +
      '<p>' + escapeHTML(text) + '</p>' +
    '</article>'
  );
}

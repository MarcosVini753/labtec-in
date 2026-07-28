import { members, projects, news, courses, materials, impactNumbers } from '../../data/data.mjs';
import { escapeHTML, renderTags, renderNewsCards, renderProjectCards, setActiveLink } from '../components/ui.mjs';
import { formatDate } from '../core/utils.js';

export function renderHome() {
  setActiveLink('#home');
  const main = document.getElementById('app');
  const latestNews = news.slice(0, 2);
  const featuredProjects = projects.slice(0, 2);

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
            '<li><strong>' + impactNumbers.projetos + '+</strong><span>projetos e iniciativas acadêmicas</span></li>' +
            '<li><strong>' + impactNumbers.membros + '+</strong><span>membros em formação científica</span></li>' +
            '<li><strong>' + impactNumbers.parcerias + '+</strong><span>parcerias para inovação aplicada</span></li>' +
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
          renderNewsCards(latestNews) +
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
          renderProjectCards(featuredProjects) +
        '</div>' +
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
          '<div class="impact-item"><span class="number">' + impactNumbers.membros + '</span><span class="label">Membros</span></div>' +
          '<div class="impact-item"><span class="number">' + impactNumbers.projetos + '</span><span class="label">Projetos</span></div>' +
          '<div class="impact-item"><span class="number">' + impactNumbers.artigos + '</span><span class="label">Artigos</span></div>' +
          '<div class="impact-item"><span class="number">' + impactNumbers.parcerias + '</span><span class="label">Parcerias</span></div>' +
        '</div>' +
      '</div>' +
    '</section>';
}

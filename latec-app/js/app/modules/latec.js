import { members, projects, news, impactNumbers } from '../../data/data.mjs';
import { escapeHTML, renderNewsCards, renderProjectCards, setActiveLink } from '../components/ui.mjs';

let styleInjected = false;

export function renderLatec() {
  setActiveLink('#latec');
  const main = document.getElementById('app');

  if (!styleInjected) {
    styleInjected = true;
    injectLatecStyles();
  }

  const latestNews = news.slice(0, 2);
  const featuredProjects = projects.slice(0, 2);

  main.innerHTML =
    '<section class="latec-hero">' +
      '<div class="container latec-hero-grid">' +
        '<div>' +
          '<p class="section-kicker">Biotecnologia, biodiversidade e inovação</p>' +
          '<h1>LATEC<span class="latec-brand-line">.IN</span></h1>' +
          '<p>Uma liga acadêmica conectando ensino, pesquisa e extensão para transformar ciência em soluções para a Amazônia.</p>' +
          '<div class="latec-hero-actions">' +
            '<a href="#portfolio" class="btn btn-primary">Conheça os projetos</a>' +
            '<a href="#contato" class="btn btn-secondary">Fale com a liga</a>' +
          '</div>' +
        '</div>' +
        '<aside class="latec-hero-panel" aria-label="Destaques da LATEC.IN">' +
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
          '<h2 class="section-title">Indicadores da LATEC.IN</h2>' +
          '<p class="section-lead">Números simulados do protótipo para representar atividade acadêmica, produção e cooperação.</p>' +
        '</div>' +
        '<div class="latec-impact-grid">' +
          '<div class="latec-impact-item"><span class="latec-number">' + impactNumbers.membros + '</span><span class="latec-label">Membros</span></div>' +
          '<div class="latec-impact-item"><span class="latec-number">' + impactNumbers.projetos + '</span><span class="latec-label">Projetos</span></div>' +
          '<div class="latec-impact-item"><span class="latec-number">' + impactNumbers.artigos + '</span><span class="latec-label">Artigos</span></div>' +
          '<div class="latec-impact-item"><span class="latec-number">' + impactNumbers.parcerias + '</span><span class="latec-label">Parcerias</span></div>' +
        '</div>' +
      '</div>' +
    '</section>';
}

function injectLatecStyles() {
  const style = document.createElement('style');
  style.textContent =
    '.latec-hero {' +
      'background:' +
        'linear-gradient(135deg, rgba(5, 22, 18, 0.96), rgba(13, 41, 22, 0.94) 54%, rgba(58, 101, 30, 0.88)),' +
        'url("data:image/svg+xml,%3Csvg width=\'160\' height=\'160\' viewBox=\'0 0 160 160\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'none\' stroke=\'%238CA685\' stroke-opacity=\'.22\'%3E%3Cpath d=\'M12 93c22-6 39-23 51-51 9 35 28 55 58 60-33 10-52 28-59 55-10-32-27-53-50-64Z\'/%3E%3Cpath d=\'M113 8c8 19 20 31 38 36-19 6-31 18-37 36-7-18-18-31-36-38 18-5 30-17 35-34Z\'/%3E%3C/g%3E%3C/svg%3E");' +
      'color: #fff;' +
      'overflow: hidden;' +
      'padding: 92px 0 72px;' +
    '}' +
    '.latec-hero-grid {' +
      'display: grid;' +
      'gap: 40px;' +
      'grid-template-columns: minmax(0, 1.25fr) minmax(280px, 0.75fr);' +
      'align-items: center;' +
    '}' +
    '.latec-hero h1 {' +
      'font-size: clamp(2.55rem, 7vw, 5.7rem);' +
      'font-weight: 900;' +
      'letter-spacing: 0;' +
      'line-height: 0.92;' +
      'margin: 0 0 20px;' +
    '}' +
    '.latec-brand-line {' +
      'color: #b9d07a;' +
      'display: block;' +
    '}' +
    '.latec-hero p {' +
      'color: rgba(255, 255, 255, 0.84);' +
      'font-size: clamp(1.05rem, 2vw, 1.28rem);' +
      'margin: 0 0 28px;' +
      'max-width: 720px;' +
    '}' +
    '.latec-hero-actions {' +
      'display: flex;' +
      'flex-wrap: wrap;' +
      'gap: 12px;' +
    '}' +
    '.latec-hero-panel {' +
      'background: rgba(255, 255, 255, 0.1);' +
      'border: 1px solid rgba(255, 255, 255, 0.16);' +
      'border-radius: 28px;' +
      'box-shadow: 0 24px 60px rgba(0, 0, 0, 0.18);' +
      'padding: 28px;' +
    '}' +
    '.latec-hero-panel strong {' +
      'color: #dcebb4;' +
      'display: block;' +
      'font-size: 2rem;' +
      'line-height: 1;' +
    '}' +
    '.latec-hero-panel span {' +
      'color: rgba(255, 255, 255, 0.78);' +
    '}' +
    '.latec-hero-panel ul {' +
      'display: grid;' +
      'gap: 18px;' +
      'list-style: none;' +
      'margin: 0;' +
      'padding: 0;' +
    '}' +
    '.latec-impact-grid {' +
      'display: grid;' +
      'gap: 18px;' +
      'grid-template-columns: repeat(auto-fit, minmax(min(100%, 180px), 1fr));' +
    '}' +
    '.latec-impact-item {' +
      'background: rgba(255, 255, 255, 0.94);' +
      'border: 1px solid rgba(212, 216, 206, 0.9);' +
      'border-radius: 16px;' +
      'box-shadow: 0 16px 42px rgba(5, 22, 18, 0.08);' +
      'padding: 22px;' +
      'text-align: center;' +
      'transition: transform 0.2s ease, box-shadow 0.2s ease;' +
    '}' +
    '.latec-impact-item:hover {' +
      'transform: translateY(-3px);' +
      'box-shadow: 0 22px 54px rgba(5, 22, 18, 0.14);' +
    '}' +
    '.latec-number {' +
      'color: #2A4F22;' +
      'display: block;' +
      'font-size: 2.1rem;' +
      'font-weight: 900;' +
      'line-height: 1;' +
    '}' +
    '.latec-label {' +
      'color: rgba(5, 22, 18, 0.72);' +
      'display: block;' +
      'font-size: 0.95rem;' +
      'margin-top: 6px;' +
    '}';
  document.head.appendChild(style);
}

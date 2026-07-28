import { escapeHTML, setActiveLink } from '../components/ui.mjs';
import { fetchHome } from '../core/api.js';

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
          '<p class="section-lead">Professores, técnicos, ligantes e pesquisadores que mantêm o lab funcionando.</p>' +
        '</div>' +
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
}

function buildPillar(title, text) {
  return (
    '<article class="card pillar-card">' +
      '<h3>' + escapeHTML(title) + '</h3>' +
      '<p>' + escapeHTML(text) + '</p>' +
    '</article>'
  );
}

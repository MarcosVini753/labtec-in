import { escapeHTML, renderTags, setActiveLink } from '../components/ui.mjs';
import { fetchPeopleList } from '../core/api.js';

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
        '</div>' +
        '<div class="card-grid" id="quem-somos-grid">' +
          '<div class="empty-state">Carregando equipe...</div>' +
        '</div>' +
      '</div>' +
    '</section>';

  fetchPeopleList()
    .then(function (items) {
      renderTeam(items);
    })
    .catch(function () {
      const teamGrid = document.getElementById('quem-somos-grid');
      if (teamGrid) teamGrid.innerHTML = '<div class="empty-state">Não foi possível carregar a equipe.</div>';
    });

  function renderTeam(items) {
    const teamGrid = document.getElementById('quem-somos-grid');
    if (!teamGrid) return;

    if (!items.length) {
      teamGrid.innerHTML = '<div class="empty-state">Nenhuma pessoa encontrada.</div>';
      return;
    }

    const normalized = items.map(function (m) {
      return {
        full_name: m.full_name || m.name || 'Membro',
        photo: m.photo || m.avatar || m.foto || '',
        memberships: Array.isArray(m.memberships) ? m.memberships : Array.isArray(m.institution_memberships) ? m.institution_memberships : [],
        short_bio: m.short_bio || m.bio || '',
      };
    });

    const grouped = {};
    normalized.forEach(function (p) {
      (p.memberships || []).forEach(function (membership) {
        const role = membership.role || 'Outros';
        if (!grouped[role]) grouped[role] = [];
        grouped[role].push(p);
      });
    });

    const roles = Object.keys(grouped);
    if (!roles.length) {
      teamGrid.innerHTML = '<div class="empty-state">Nenhuma pessoa encontrada.</div>';
      return;
    }

    teamGrid.innerHTML = roles
      .map(function (role) {
        const peopleInRole = grouped[role] || [];
        const cards = peopleInRole
          .map(function (p) {
            const name = escapeHTML(p.full_name);
            const photo = escapeHTML(p.photo);
            const bio = escapeHTML((p.short_bio || '').replace(/<[^>]+>/g, ''));
            return (
              '<article class="card">' +
                (photo ? '<img class="card-media" src="' + photo + '" alt="Foto de ' + name + '">' : '') +
                '<h3>' + name + '</h3>' +
                '<p>' + (bio || '') + '</p>' +
              '</article>'
            );
          })
          .join('');
        return '<h3>' + escapeHTML(role) + '</h3><div class="card-grid">' + cards + '</div>';
      })
      .join('');
  }
}

import { escapeHTML, setActiveLink, renderNewsCards } from '../components/ui.mjs';
import { formatDate } from '../core/utils.js';
import { fetchPosts } from '../core/api.js';

export function renderNoticias() {
  setActiveLink('#noticias');
  const main = document.getElementById('app');
  main.innerHTML =
    '<section class="page-section">' +
      '<div class="container">' +
        '<div class="section-heading">' +
          '<p class="section-kicker">Comunicação</p>' +
          '<h2 class="section-title">Notícias e Publicações</h2>' +
          '<p class="section-lead">Acompanhe editais, eventos e publicações da LATEC.IN.</p>' +
        '</div>' +
        '<div class="card-grid" id="noticias-grid">' +
          '<div class="empty-state">Carregando notícias...</div>' +
        '</div>' +
      '</div>' +
    '</section>';

  fetchPosts()
    .then(function (items) {
      const grid = document.getElementById('noticias-grid');
      if (!grid) return;
      grid.innerHTML = items.length ? renderNewsCards(items) : '<div class="empty-state">Nenhuma notícia publicada.</div>';
    })
    .catch(function () {
      const grid = document.getElementById('noticias-grid');
      if (grid) grid.innerHTML = '<div class="empty-state">Não foi possível carregar as notícias.</div>';
    });
}

export function renderNewsDetail(id) {
  setActiveLink(null);
  const main = document.getElementById('app');

  fetchPosts()
    .then(function (posts) {
      const post = posts.find(function (n) { return String(n.id) === String(id); });
      if (!post) {
        renderNotFound();
        return;
      }

      const categoria = post.axis && post.axis.name ? post.axis.name : (post.category || 'Notícia');
      const data = formatDate(post.published_at || '');
      const imagem = post.cover_image
        ? '<img src="' + escapeHTML(post.cover_image) + '" alt="' + escapeHTML(post.title || 'Notícia') + '">'
        : '';

      main.innerHTML =
        '<section class="page-section">' +
          '<div class="container">' +
            '<div class="detail-actions">' +
              '<a href="#noticias" class="btn btn-secondary">Voltar para Notícias</a>' +
            '</div>' +
            '<article class="content-panel detail-panel prose">' +
              '<p class="section-kicker">' + escapeHTML(categoria) + (data ? ' - ' + escapeHTML(data) : '') + '</p>' +
              '<h2 class="section-title">' + escapeHTML(post.title || 'Notícia') + '</h2>' +
              imagem +
              '<p>' + escapeHTML(post.content || post.summary || '') + '</p>' +
            '</article>' +
          '</div>' +
        '</section>';
    })
    .catch(function () {
      renderNotFound();
    });
}

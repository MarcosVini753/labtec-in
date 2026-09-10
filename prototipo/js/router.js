/*
  router.js
  Define as regras de navegação baseadas no fragmento da URL (#hash).
  Sempre que o hash muda, ou quando a página é carregada, a função router
  identifica qual view deve ser renderizada e delega para a função adequada
  em render.js.
*/

function router() {
  const hash = window.location.hash || '#home';
  // Trata parâmetros na URL (ex: #projeto?id=1)
  const [route, queryString] = hash.split('?');
  const params = new URLSearchParams(queryString);
  switch (true) {
    // Página interna de projeto
    case /^#projeto\b/.test(route): {
      const id = parseInt(params.get('id'), 10);
      if (!isNaN(id)) {
        renderProjectDetail(id);
      } else {
        renderNotFound();
      }
      break;
    }
    // Página interna de notícia
    case /^#noticia\b/.test(route): {
      const id = parseInt(params.get('id'), 10);
      if (!isNaN(id)) {
        renderNewsDetail(id);
      } else {
        renderNotFound();
      }
      break;
    }
    default: {
      // Rotas principais
      switch (route) {
        case '#home':
          renderHome();
          break;
        case '#quem-somos':
          renderQuemSomos();
          break;
        case '#portfolio':
          renderPortfolio();
          break;
        case '#capacitacao':
          renderCapacitacao();
          break;
        case '#noticias':
          renderNoticias();
          break;
        case '#contato':
          renderContato();
          break;
        case '#admin':
          renderAdmin();
          break;
        default:
          // rota desconhecida
          renderNotFound();
      }
    }
  }
}

// Inicializa o roteador nas mudanças de hash e no carregamento inicial
window.addEventListener('hashchange', router);
window.addEventListener('load', router);
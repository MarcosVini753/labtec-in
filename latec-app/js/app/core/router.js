import { renderHome } from '../modules/home.js';
import { renderLatec } from '../modules/latec.js';
import { renderQuemSomos } from '../modules/quem-somos.js';
import { renderPortfolio, renderProjectDetail } from '../modules/portfolio.js';
import { renderCapacitacao } from '../modules/capacitacao.js';
import { renderNoticias, renderNewsDetail } from '../modules/noticias.js';
import { renderContato } from '../modules/contato.js';

function router() {
  const hash = window.location.hash || '#home';
  const [route, queryString] = hash.split('?');
  const params = new URLSearchParams(queryString);

  switch (true) {
    case /^#projeto\b/.test(route): {
      const id = parseInt(params.get('id'), 10);
      if (!isNaN(id)) {
        renderProjectDetail(id);
      } else {
        renderPortfolio();
      }
      break;
    }
    case /^#noticia\b/.test(route): {
      const id = parseInt(params.get('id'), 10);
      if (!isNaN(id)) {
        renderNewsDetail(id);
      } else {
        renderNoticias();
      }
      break;
    }
    default:
      switch (route) {
        case '#home': renderHome(); break;
        case '#laboratorio': renderHome('#laboratorio'); break;
        case '#latec': renderLatec(); break;
        case '#quem-somos': renderQuemSomos(); break;
        case '#portfolio': renderPortfolio(); break;
        case '#capacitacao': renderCapacitacao(); break;
        case '#noticias': renderNoticias(); break;
        case '#contato': renderContato(); break;
        default: renderHome();
      }
  }
}

window.addEventListener('hashchange', router);
window.addEventListener('load', router);

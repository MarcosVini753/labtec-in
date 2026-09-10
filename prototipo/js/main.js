/*
  main.js
  Ponto de entrada do protótipo. Configura comportamentos globais,
  como o menu mobile, carrega dados persistidos e inicializa o roteador.
*/

document.addEventListener('DOMContentLoaded', () => {
  // Menu mobile: alterna exibição da navegação
  const toggleButton = document.getElementById('mobile-menu-toggle');
  const nav = document.getElementById('main-nav');
  toggleButton.addEventListener('click', () => {
    nav.classList.toggle('open');
    toggleButton.setAttribute('aria-expanded', nav.classList.contains('open') ? 'true' : 'false');
  });
  // Fecha o menu ao clicar em um link
  document.querySelectorAll('.main-nav a').forEach(link => {
    link.addEventListener('click', () => {
      nav.classList.remove('open');
      toggleButton.setAttribute('aria-expanded', 'false');
    });
  });
  // Carrega dados salvos localmente, se disponíveis (Admin)
  if (typeof loadStoredData === 'function') {
    loadStoredData();
  }
});

/*
  filters.js
  Define funções auxiliares para filtragem de coleções de dados, como
  projetos ou notícias. Embora o portfólio implemente seus próprios filtros,
  estas funções podem ser reutilizadas em outras partes do protótipo.
*/

/**
 * Filtra uma lista de projetos pelo campo categoria.
 * @param {String} categoria - nome da categoria (Ex: 'Pesquisa')
 * @param {Array} lista - lista de projetos
 * @returns {Array} array filtrado
 */
function filtrarPorCategoria(categoria, lista) {
  if (!categoria || categoria.toLowerCase() === 'todos') return lista;
  return lista.filter(item => (item.categoria || '').toLowerCase() === categoria.toLowerCase());
}

/**
 * Filtra uma lista de itens por termo de pesquisa em campos texto.
 * @param {String} termo - termo a buscar
 * @param {Array} lista - lista de itens com campo 'titulo' ou 'nome'
 * @returns {Array} array filtrado
 */
function filtrarPorBusca(termo, lista) {
  if (!termo) return lista;
  const t = termo.toLowerCase();
  return lista.filter(item => {
    const texto = (item.titulo || item.nome || '').toLowerCase();
    return texto.includes(t);
  });
}
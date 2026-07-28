const API_BASE = 'http://127.0.0.1:8000/api/v1/site/home';
const PEOPLE_API = 'http://127.0.0.1:8000/api/v1/people';

async function loadJSON(path) {
  const response = await fetch(path, { headers: { Accept: 'application/json' } });
  if (!response.ok) throw new Error('Falha ao carregar ' + path + ': ' + response.status);
  return response.json();
}

export async function fetchHome() {
  return loadJSON(API_BASE);
}

export async function fetchPeople() {
  const data = await fetchHome();
  return Array.isArray(data.people) ? data.people : [];
}

export async function fetchPeopleList(params) {
  const query = new URLSearchParams();
  const withMemberships = (params && params.withMemberships) !== false;
  if (withMemberships) query.set('with_memberships', '1');

  const path = PEOPLE_API + (query.toString() ? '?' + query.toString() : '');
  const data = await loadJSON(path);
  return Array.isArray(data.results) ? data.results : Array.isArray(data) ? data : [];
}

export async function fetchPosts() {
  const data = await fetchHome();
  return Array.isArray(data.posts) ? data.posts : [];
}

export async function fetchProjects() {
  const data = await fetchHome();
  return Array.isArray(data.projects) ? data.projects : [];
}

export async function fetchImpactMetrics() {
  const data = await fetchHome();
  return Array.isArray(data.impact_metrics) ? data.impact_metrics : [];
}

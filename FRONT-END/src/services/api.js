const API = import.meta.env.VITE_API_URL || 'https://api.example.com';

async function request(path, opts = {}) {
  const url = `${API}${path}`;
  const res = await fetch(url, opts);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json().catch(() => null);
}

export async function login(email, password) {
  return request('/auth/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password }) });
}

export async function fetchStores() {
  return request('/stores');
}

export async function fetchStore(idOrSlug) {
  return request(`/stores/${idOrSlug}`);
}

export async function fetchProducts(storeId) {
  return request(`/stores/${storeId}/products`);
}

export async function fetchProduct(storeId, productId) {
  return request(`/stores/${storeId}/products/${productId}`);
}

export async function calculateShipping(toZip, items) {
  // backend integration expected; placeholder
  return request(`/shipping/calculate`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ toZip, items }) });
}

export async function createPixPayment(order) {
  return request('/payments/pix', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(order) });
}

export async function createOrder(order) {
  return request('/orders', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(order) });
}

export default { request };

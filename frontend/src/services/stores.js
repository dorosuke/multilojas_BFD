import { getApi } from './api'

export async function listStores() {
  return getApi('/lojas/')
}

export async function getStoreDetail(id, { page = 1, pageSize = 12 } = {}) {
  return getApi(`/lojas/${id}/`, { params: { page, page_size: pageSize } })
}

export async function getStoreProducts(id, { page = 1, pageSize = 12, category, sort } = {}) {
  return getApi(`/lojas/${id}/produtos/`, {
    params: {
      page,
      page_size: pageSize,
      category: category ?? undefined,
      sort: sort ?? undefined,
    },
  })
}

export async function getShowcase({ perStore = 8 } = {}) {
  return getApi('/vitrine/', { params: { per_store: perStore } })
}

export async function getPublicProduct(id) {
  return getApi(`/produtos/${id}/`)
}

export async function searchProducts({
  q = '',
  categories = [],
  stores = [],
  minPrice,
  maxPrice,
  sort = 'relevance',
  page = 1,
  pageSize = 24
} = {}) {
  return getApi('/busca/', {
    params: {
      q,
      categories: categories.length ? categories.join(',') : undefined,
      stores: stores.length ? stores.join(',') : undefined,
      min_price: minPrice ?? undefined,
      max_price: maxPrice ?? undefined,
      sort,
      page,
      page_size: pageSize
    }
  })
}

export async function getSearchFilters({ q = '' } = {}) {
  return getApi('/busca/filtros/', { params: { q } })
}

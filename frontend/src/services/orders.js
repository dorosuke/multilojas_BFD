import { postApi } from './api'

export async function createOrder({ store_id, shipping_address, items }) {
  return postApi('/orders/', {
    store_id,
    shipping_address,
    items,
  })
}


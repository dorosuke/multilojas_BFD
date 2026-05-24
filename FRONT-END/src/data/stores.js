const stores = [
  {
    id: 1,
    name: 'Aurora Modas',
    category: 'Roupas',
    location: 'São Paulo, SP',
    description: 'Moda feminina e masculina — peças casuais e formais.',
    products: [
      { id: 'r1', name: 'Vestido Floral', price: 129.9, images: ['https://source.unsplash.com/800x600/?dress,floral','https://source.unsplash.com/800x600/?dress,fashion','https://source.unsplash.com/800x600/?women%20dress'] },
      { id: 'r2', name: 'Camisa Social', price: 89.9, images: ['https://source.unsplash.com/800x600/?shirt,formal','https://source.unsplash.com/800x600/?shirt,men','https://source.unsplash.com/800x600/?dress%20shirt'] },
      { id: 'r3', name: 'Calça Jeans', price: 119.0, images: ['https://source.unsplash.com/800x600/?jeans,denim','https://source.unsplash.com/800x600/?denim,jeans','https://source.unsplash.com/800x600/?blue%20jeans'] }
    ]
  },
  {
    id: 2,
    name: 'Tempo Fino',
    category: 'Relógios',
    location: 'Rio de Janeiro, RJ',
    description: 'Relógios analógicos e digitais — clássicos e esportivos.',
    products: [
      { id: 'w1', name: 'Relógio Clássico', price: 499.0, images: ['https://source.unsplash.com/800x600/?watch,classic','https://source.unsplash.com/800x600/?vintage%20watch','https://source.unsplash.com/800x600/?analog%20watch'] },
      { id: 'w2', name: 'Smartwatch Sport', price: 899.0, images: ['https://source.unsplash.com/800x600/?smartwatch,sport','https://source.unsplash.com/800x600/?smartwatch,fitness','https://source.unsplash.com/800x600/?fitness%20watch'] },
      { id: 'w3', name: 'Relógio Minimal', price: 299.0, images: ['https://source.unsplash.com/800x600/?minimal%20watch','https://source.unsplash.com/800x600/?simple%20watch','https://source.unsplash.com/800x600/?minimalist%20watch'] }
    ]
  },
  {
    id: 3,
    name: 'Essência Pura',
    category: 'Perfumes',
    location: 'Belo Horizonte, MG',
    description: 'Perfumes importados e nacionais — coleções para presente.',
    products: [
      { id: 'p1', name: 'Eau de Parfum 50ml', price: 249.9, images: ['https://source.unsplash.com/800x600/?perfume,fragrance','https://source.unsplash.com/800x600/?perfume,bottle','https://source.unsplash.com/800x600/?fragrance'] },
      { id: 'p2', name: 'Colônia 100ml', price: 179.9, images: ['https://source.unsplash.com/800x600/?cologne,perfume','https://source.unsplash.com/800x600/?cologne,bottle','https://source.unsplash.com/800x600/?men%20cologne'] },
      { id: 'p3', name: 'Kit Presente', price: 319.0, images: ['https://source.unsplash.com/800x600/?gift%20set,perfume','https://source.unsplash.com/800x600/?gift%20box,fragrance','https://source.unsplash.com/800x600/?present%20set'] }
    ]
  },
  {
    id: 4,
    name: 'Boné Central',
    category: 'Acessórios',
    location: 'Curitiba, PR',
    description: 'Bonés, chapéus e acessórios para todos os estilos.',
    products: [
      { id: 'b1', name: 'Boné Snapback', price: 59.9, images: ['https://source.unsplash.com/800x600/?cap,snapback','https://source.unsplash.com/800x600/?cap,hat','https://source.unsplash.com/800x600/?snapback'] },
      { id: 'b2', name: 'Chapéu Panamá', price: 89.9, images: ['https://source.unsplash.com/800x600/?panama,hat','https://source.unsplash.com/800x600/?hat,panama','https://source.unsplash.com/800x600/?panama%20hat'] }
    ]
  },
  // Novo card extra
  {
    id: 5,
    name: 'Tech Mania',
    category: 'Eletrônicos',
    location: 'Florianópolis, SC',
    description: 'Gadgets, acessórios e novidades em tecnologia.',
    products: [
      { id: 't1', name: 'Fone Bluetooth', price: 149.9, images: ['https://source.unsplash.com/800x600/?headphone,bluetooth','https://source.unsplash.com/800x600/?earbuds,tech'] },
      { id: 't2', name: 'Smart Speaker', price: 299.0, images: ['https://source.unsplash.com/800x600/?smart,speaker','https://source.unsplash.com/800x600/?speaker,tech'] }
    ]
  }
  // Se quiser adicionar mais lojas, adicione aqui, garantindo ids únicos
];

export default stores;

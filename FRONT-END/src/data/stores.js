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
    category: 'Bones',
    location: 'Curitiba, PR',
    description: 'Bonés e acessórios streetwear — diversas marcas e estilos.',
    products: [
      { id: 'b1', name: 'Boné Snapback', price: 79.9, images: ['https://source.unsplash.com/800x600/?cap,snapback','https://source.unsplash.com/800x600/?snapback,cap','https://source.unsplash.com/800x600/?baseball%20cap'] },
      { id: 'b2', name: 'Boné Trucker', price: 69.9, images: ['https://source.unsplash.com/800x600/?trucker%20cap,cap','https://source.unsplash.com/800x600/?truckercap','https://source.unsplash.com/800x600/?cap,truck'] },
      { id: 'b3', name: 'Boné Aba Curva', price: 59.9, images: ['https://source.unsplash.com/800x600/?curved%20cap,cap','https://source.unsplash.com/800x600/?cap,curved','https://source.unsplash.com/800x600/?cap,style'] }
    ]
  },
  {
    id: 5,
    name: 'Mix Store',
    category: 'Multicategory',
    location: 'Porto Alegre, RS',
    description: 'Loja multiuso com roupas, relógios, perfumes e acessórios.',
    products: [
      { id: 'm1', name: 'Camiseta Básica', price: 49.9, images: ['https://source.unsplash.com/800x600/?tshirt,casual','https://source.unsplash.com/800x600/?tee,shirt','https://source.unsplash.com/800x600/?casual%20tshirt'] },
      { id: 'm2', name: 'Relógio Casual', price: 249.0, images: ['https://source.unsplash.com/800x600/?watch,casual','https://source.unsplash.com/800x600/?casual%20watch','https://source.unsplash.com/800x600/?everyday%20watch'] },
      { id: 'm3', name: 'Perfume Unissex 50ml', price: 199.9, images: ['https://source.unsplash.com/800x600/?unisex%20perfume,fragrance','https://source.unsplash.com/800x600/?perfume,unisex','https://source.unsplash.com/800x600/?fragrance,unisex'] }
    ]
  }
];

export default stores;

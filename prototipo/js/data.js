/*
  Este arquivo contém dados simulados para o protótipo da plataforma LATEC.IN.
  Em uma aplicação real, essas informações seriam buscadas de um banco de dados
  ou API. Aqui utilizamos objetos e arrays estáticos para facilitar a
  demonstração da navegação e dos filtros.
*/

// Membros da liga
const members = [
  {
    id: 1,
    nome: 'Marta Adelino',
    funcao: 'Coordenadora',
    bio: 'Professora doutora e coordenadora da LATEC.IN, com larga experiência em biotecnologia e gestão de projetos.',
    foto: 'js/pics/marta.png'
  },
  {
    id: 2,
    nome: 'Gabriel Daniel',
    funcao: 'Estagiário',
    bio: 'Estudante de Sistemas de Informação na UFAC, responsável pela criação deste protótipo.',
    foto: 'js/pics/gabriel.png'
  },
  {
    id: 3,
    nome: 'Ana Souza',
    funcao: 'Pesquisadora',
    bio: 'Discente pesquisadora focada em bioinformática e biodiversidade amazônica.',
    foto: 'js/pics/ana.png'
  },
  {
    id: 4,
    nome: 'Marcos Moraes',
    funcao: 'Ligante',
    bio: 'Estudante de Sistemas de Informação na UFAC, responsável pela criação deste protótipo.',
    foto: 'js/pics/marcos.png'
  },
  {
    id: 5,
    nome: 'Kleyton Passos',
    funcao: 'Professor',
    bio: 'Dr. em Ciências da Saúde',
    foto: 'js/pics/kleyton.png'
  },
  {
    id: 6,
    nome: 'Luciana Castello',
    funcao: 'Professor',
    bio: 'Engenheira de alimentos e Dra. em Ciência de Alimentos',
    foto: 'js/pics/luciana.png'
  },
  {
    id: 7,
    nome: 'Bruno Favero',
    funcao: 'Professor',
    bio: 'Engenheiro Agronômico e Dr. em Botânica',
    foto: 'js/pics/bruno.png'
  },
  {
    id: 8,
    nome: 'Dayam Marques',
    funcao: 'Professor',
    bio: 'Farmacêutico e Mestre em Quimica',
    foto: 'js/pics/dayam.png'
  },
  {
    id: 9,
    nome: 'Anne Grace',
    funcao: 'Professor',
    bio: 'Enfermeira, Mestre em Educação e Tecnologias de Enfermagem',
    foto: 'js/pics/anne.png'
  },
  {
    id: 10,
    nome: 'Almecina Balbino',
    funcao: 'Professor',
    bio: 'Engenheira Agrônoma e Dra. em Horticultura',
    foto: 'js/pics/almecina.png'
  },
  {
    id: 11,
    nome: 'Marilene Lima',
    funcao: 'Professor',
    bio: 'Engenheira Agrônoma e Dra. em Fitotecnia',
    foto: 'js/pics/marilene.png'
  },
  {
    id: 12,
    nome: 'Bruna Viana',
    funcao: 'Professor',
    bio: 'Nutricionista, Dra. em sanidade e produção animal sustentável na Amazônia Ocidental',
    foto: 'js/pics/bruna.png'
  },
  {
    id: 13,
    nome: 'Adson Jhonnata Lima Ferreira',
    funcao: 'Ligante',
    bio: '',
    foto: 'js/pics/Adson Jhonnata Lima Ferreira.jpeg'
  },
  {
    id: 14,
    nome: 'Ana Clara Souza',
    funcao: 'Ligante',
    bio: '',
    foto: 'js/pics/Ana Clara Souza.jpeg'
  },
  {
    id: 15,
    nome: 'Ana Vivyan Ferreira Cavalcante',
    funcao: 'Ligante',
    bio: '',
    foto: 'js/pics/Ana Vivyan Ferreira Cavalcante.jpeg'
  },
  {
    id: 16,
    nome: 'Andrick Alexandre de Oliveira',
    funcao: 'Ligante',
    bio: '',
    foto: 'js/pics/Andrick Alexandre de Oliveira.jpeg'
  },
  {
    id: 17,
    nome: 'Bruno Carvalho dos Santos',
    funcao: 'Ligante',
    bio: '',
    foto: 'js/pics/Bruno Carvalho dos Santos.jpeg'
  },
  {
    id: 18,
    nome: 'Cristielen Frota',
    funcao: 'Ligante',
    bio: '',
    foto: 'js/pics/Cristielen Frota.jpeg'
  },
  {
    id: 19,
    nome: 'Débora Rocha de Mesquita',
    funcao: 'Ligante',
    bio: '',
    foto: 'js/pics/Débora Rocha de Mesquita.jpeg'
  },
  {
    id: 20,
    nome: 'Deborah da Silva Lima',
    funcao: 'Ligante',
    bio: '',
    foto: 'js/pics/Deborah da Silva Lima.jpeg'
  },
  {
    id: 21,
    nome: 'Eduardo dos Santos Feitosa',
    funcao: 'Ligante',
    bio: '',
    foto: 'js/pics/Eduardo dos Santos Feitosa.jpeg'
  },
  {
    id: 22,
    nome: 'Eshyla Maria da Silva Maia',
    funcao: 'Ligante',
    bio: '',
    foto: 'js/pics/Eshyla Maria da Silva Maia.jpeg'
  },
  {
    id: 23,
    nome: 'Felipe Gabriel Dantas Azevedo',
    funcao: 'Ligante',
    bio: '',
    foto: 'js/pics/Felipe Gabriel Dantas Azevedo.jpeg'
  },
  {
    id: 24,
    nome: 'Laíza Rivera de Sousa',
    funcao: 'Ligante',
    bio: '',
    foto: 'js/pics/Laíza Rivera de Sousa.jpeg'
  },
  {
    id: 25,
    nome: 'Lougan Coelho Alves',
    funcao: 'Ligante',
    bio: '',
    foto: 'js/pics/Lougan Coelho Alves.jpeg'
  },
  {
    id: 26,
    nome: 'Mary Anny Mariscal',
    funcao: 'Ligante',
    bio: '',
    foto: 'js/pics/Mary Anny Mariscal.jpeg'
  },
  {
    id: 27,
    nome: 'Mirela Brito',
    funcao: 'Ligante',
    bio: '',
    foto: 'js/pics/Mirela Brito.jpeg'
  },
  {
    id: 28,
    nome: 'Sabrina Brasil de Oliveira',
    funcao: 'Ligante',
    bio: '',
    foto: 'js/pics/Sabrina Brasil de Oliveira.jpeg'
  },
  {
    id: 29,
    nome: 'Salvino de Castro',
    funcao: 'Ligante',
    bio: '',
    foto: 'js/pics/Salvino de Castro.jpeg'
  },
  {
    id: 30,
    nome: 'Stéphany Portela',
    funcao: 'Ligante',
    bio: '',
    foto: 'js/pics/Stéphany Portela.jpeg'
  },
  {
    id: 31,
    nome: 'Suzanne Hadassa Da Silva Lima',
    funcao: 'Ligante',
    bio: '',
    foto: 'js/pics/Suzanne Hadassa Da Silva Lima.jpeg'
  },
  {
    id: 32,
    nome: 'Thais Cristina Silva Filgueira Monteiro',
    funcao: 'Ligante',
    bio: '',
    foto: 'js/pics/Thais Cristina Silva Filgueira Monteiro.jpeg'
  },
  {
    id: 33,
    nome: 'Thiago Schuster Casas',
    funcao: 'Ligante',
    bio: '',
    foto: 'js/pics/Thiago Schuster Casas.jpeg'
  }
];

// Projetos desenvolvidos
const projects = [
  {
    id: 1,
    titulo: 'Fábrica de Ensino: Bootcamp de Startups',
    categoria: 'Ensino',
    area: 'Fábrica de Ensino',
    status: 'Concluído',
    ano: 2025,
    resumo: 'Bootcamp intensivo de Startups para novos membros da LATEC.IN.',
    problema: 'Falta de capacitação em desenvolvimento de negócios entre os integrantes.',
    solucao: 'Proporcionar um treinamento prático e imersivo em desenvolvimento de startups.',
    resultados: ['Relatório de atividades', 'Apostila digital'],
    equipe: [1, 2, 3],
    link: ''
  },
  {
    id: 2,
    titulo: 'Pesquisa de Bioativos da Amazônia',
    categoria: 'Pesquisa',
    area: 'Projetos de Pesquisa',
    status: 'Em andamento',
    ano: 2026,
    resumo: 'Estudo dos compostos bioativos presentes em espécies amazônicas.',
    problema: 'Necessidade de explorar novos fármacos e compostos naturais.',
    solucao: 'Investigar propriedades bioativas de plantas da região amazônica.',
    resultados: ['Artigo científico', 'Protótipo de extrato'],
    equipe: [1, 3],
    link: ''
  },
  {
    id: 3,
    titulo: 'Extensão em Tecnologias Sustentáveis',
    categoria: 'Extensão',
    area: 'Extensão Tecnológica',
    status: 'Planejado',
    ano: 2026,
    resumo: 'Iniciativa para aplicar tecnologia verde em comunidades locais.',
    problema: 'Falta de acesso a tecnologias sustentáveis em regiões remotas.',
    solucao: 'Desenvolver protótipos de baixo custo e treinamentos comunitários.',
    resultados: ['Manual de boas práticas'],
    equipe: [2, 3],
    link: ''
  }
];

// Notícias / artigos
const news = [
  {
    id: 1,
    titulo: 'Coordenadora do LATEC.IN é premiada por inovação tecnológica',
    data: '2026-05-29',
    resumo: 'A professora Marta Adelino recebeu o prêmio de inovação tecnológica da UFAC por seu trabalho à frente da LATEC.IN.',
    conteudo: 'A coordenadora da LATEC.IN, professora Marta Adelino, foi reconhecida com o prêmio de inovação tecnológica da Universidade Federal do Acre (UFAC) em 2026. O prêmio destaca sua liderança e os resultados alcançados pela liga em projetos de ensino, pesquisa e extensão. A cerimônia de premiação ocorreu no auditório central da UFAC, onde Marta recebeu um certificado e um troféu em reconhecimento ao seu trabalho inovador.',
    imagem: 'js/pics/certificado.png'
  },
  {
    id: 2,
    titulo: 'LATEC.IN participa do congresso nacional de inovação',
    data: '2026-05-15',
    resumo: 'A LATEC.IN apresentou três projetos no congresso nacional, recebendo destaque na sessão de biotecnologia.',
    conteudo: 'No congresso nacional de inovação tecnológica, a LATEC.IN foi representada pelos projetos “Fábrica de Ensino”, “Pesquisa de Bioativos da Amazônia” e “Extensão em Tecnologias Sustentáveis”. As apresentações foram bem recebidas e destacaram o potencial dos alunos da UFAC.',
    imagem: 'https://via.placeholder.com/400x200?text=Congresso'
  }
];

// Cursos e capacitações
const courses = [
  {
    id: 1,
    titulo: 'Nanotecnologias de cosméticos',
    descricao: 'Aprenda sobre as aplicações de nanotecnologia na indústria cosmética.',
    data: '2026-07-10',
    status: 'Inscrições abertas',
    materiais: ['Apostila Nanotecnologia.pdf'],
    link: ''
  },
  {
    id: 2,
    titulo: 'Workshop de ML em Biotecnologia',
    descricao: 'Fundamentos de IA e Machine Learning aplicados à biotecnologia.',
    data: '2026-08-15',
    status: 'Em breve',
    materiais: [],
    link: ''
  }
];

// Materiais de apoio
const materials = [
  {
    id: 1,
    titulo: 'Apostila de Nanotecnologia',
    descricao: 'Apostila utilizada no curso de Nanotecnologia da LATEC.IN.',
    arquivo: 'assets/images/apostila-nanotecnologia.pdf'
  }
];

// Premiações e honrarias
const awards = [
  {
    id: 1,
    titulo: 'Prêmio Inovação UFAC 2025',
    descricao: 'Projeto Fábrica de Ensino premiado no evento de inovação da UFAC em 2025.',
    data: '2025-11-20'
  }
];

// Números de impacto para o painel dinâmico
const impactNumbers = {
  membros: 33,
  projetos: 20,
  artigos: 12,
  parcerias: 5
};

// Exportação global para facilitar o acesso nos arquivos de renderização
// (em ambiente real usaríamos módulos ou bundlers)
window.members = members;
window.projects = projects;
window.news = news;
window.courses = courses;
window.materials = materials;
window.awards = awards;
window.impactNumbers = impactNumbers;
from datetime import date, datetime, time
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from apps.axes.models import AxisMentorship, ResearchAxis
from apps.common.models import EditorialStatus
from apps.core.models import HeroBanner, InstitutionalSection, SiteSettings
from apps.institutional.models import InstitutionMembership, InstitutionalUnit
from apps.learning.models import Course, CourseMaterial
from apps.metrics.models import ImpactMetric
from apps.news.models import Post, PostLink
from apps.people.models import Person
from apps.portfolio.models import (
    Project,
    ProjectCategory,
    ProjectLink,
    ProjectResult,
    ProjectStartupProfile,
    ProjectStatus,
    ProjectTeamMember,
)
from apps.research.models import ResearchProject, ResearchProjectMember


PEOPLE = [
    (1, "Marta Adelino", "Coordenadora", "Professora doutora e coordenadora do LABTEC.IN e da LATEC, com larga experiência em biotecnologia e gestão de projetos.", "people/marta.png"),
    (2, "Gabriel Daniel", "Estagiário", "Estudante de Sistemas de Informação na UFAC, responsável pela criação deste protótipo.", "people/gabriel.png"),
    (3, "Ana Souza", "Pesquisador", "Discente pesquisadora focada em bioinformática e biodiversidade amazônica.", "people/ana.png"),
    (4, "Marcos Moraes", "Ligante", "Estudante de Sistemas de Informação na UFAC, responsável pela criação deste protótipo.", "people/marcos.png"),
    (5, "Kleyton Passos", "Professor", "Dr. em Ciências da Saúde", "people/kleyton.png"),
    (6, "Luciana Castello", "Professor", "Engenheira de alimentos e Dra. em Ciência de Alimentos", "people/luciana.png"),
    (7, "Bruno Favero", "Professor", "Engenheiro Agronômico e Dr. em Botânica", "people/bruno.png"),
    (8, "Dayam Marques", "Professor", "Farmacêutico e Mestre em Quimica", "people/dayam.png"),
    (9, "Anne Grace", "Professor", "Enfermeira, Mestre em Educação e Tecnologias de Enfermagem", "people/anne.png"),
    (10, "Almecina Balbino", "Professor", "Engenheira Agrônoma e Dra. em Horticultura", "people/almecina.png"),
    (11, "Marilene Lima", "Professor", "Engenheira Agrônoma e Dra. em Fitotecnia", "people/marilene.png"),
    (12, "Bruna Viana", "Professor", "Nutricionista, Dra. em sanidade e produção animal sustentável na Amazônia Ocidental", "people/bruna.png"),
    (13, "Adson Jhonnata Lima Ferreira", "Ligante", "", "people/Adson Jhonnata Lima Ferreira.jpeg"),
    (14, "Ana Clara Souza", "Ligante", "", "people/Ana Clara Souza.jpeg"),
    (15, "Ana Vivyan Ferreira Cavalcante", "Ligante", "", "people/Ana Vivyan Ferreira Cavalcante.jpeg"),
    (16, "Andrick Alexandre de Oliveira", "Ligante", "", "people/Andrick Alexandre de Oliveira.jpeg"),
    (17, "Bruno Carvalho dos Santos", "Ligante", "", "people/Bruno Carvalho dos Santos.jpeg"),
    (18, "Cristielen Frota", "Ligante", "", "people/Cristielen Frota.jpeg"),
    (19, "Débora Rocha de Mesquita", "Ligante", "", "people/Débora Rocha de Mesquita.jpeg"),
    (20, "Deborah da Silva Lima", "Ligante", "", "people/Deborah da Silva Lima.jpeg"),
    (21, "Eduardo dos Santos Feitosa", "Ligante", "", "people/Eduardo dos Santos Feitosa.jpeg"),
    (22, "Eshyla Maria da Silva Maia", "Ligante", "", "people/Eshyla Maria da Silva Maia.jpeg"),
    (23, "Felipe Gabriel Dantas Azevedo", "Ligante", "", "people/Felipe Gabriel Dantas Azevedo.jpeg"),
    (24, "Laíza Rivera de Sousa", "Ligante", "", "people/Laíza Rivera de Sousa.jpeg"),
    (25, "Lougan Coelho Alves", "Ligante", "", "people/Lougan Coelho Alves.jpeg"),
    (26, "Mary Anny Mariscal", "Ligante", "", "people/Mary Anny Mariscal.jpeg"),
    (27, "Mirela Brito", "Ligante", "", "people/Mirela Brito.jpeg"),
    (28, "Sabrina Brasil de Oliveira", "Ligante", "", "people/Sabrina Brasil de Oliveira.jpeg"),
    (29, "Salvino de Castro", "Ligante", "", "people/Salvino de Castro.jpeg"),
    (30, "Stéphany Portela", "Ligante", "", "people/Stéphany Portela.jpeg"),
    (31, "Suzanne Hadassa Da Silva Lima", "Ligante", "", "people/Suzanne Hadassa Da Silva Lima.jpeg"),
    (32, "Thais Cristina Silva Filgueira Monteiro", "Ligante", "", "people/Thais Cristina Silva Filgueira Monteiro.jpeg"),
    (33, "Thiago Schuster Casas", "Ligante", "", "people/Thiago Schuster Casas.jpeg"),
]

STARTUP_PEOPLE = [
    "José Luiz Bezerra de Faria Filho",
    "Roberta de Freitas Lopes",
    "Matheus Matos do Nascimento",
]

PROJECTS = [
    {
        "title": "Fábrica de Ensino: Bootcamp de Startups",
        "category": "Ensino",
        "area": "Fábrica de Ensino",
        "status": "Concluído",
        "year": 2025,
        "summary": "Bootcamp intensivo de Startups para novos membros da LATEC.",
        "problem": "Falta de capacitação em desenvolvimento de negócios entre os integrantes.",
        "solution": "Proporcionar um treinamento prático e imersivo em desenvolvimento de startups.",
        "results": ["Relatório de atividades", "Apostila digital"],
        "team": [1, 2, 3],
        "link": "",
    },
    {
        "title": "Extensão em Tecnologias Sustentáveis",
        "category": "Extensão",
        "area": "Extensão Tecnológica",
        "status": "Planejado",
        "year": 2026,
        "summary": "Iniciativa para aplicar tecnologia verde em comunidades locais.",
        "problem": "Falta de acesso a tecnologias sustentáveis em regiões remotas.",
        "solution": "Desenvolver protótipos de baixo custo e treinamentos comunitários.",
        "results": ["Manual de boas práticas"],
        "team": [2, 3],
        "link": "",
    },
    {
        "title": "Farma Amazônia",
        "category": "Startup",
        "area": "Fitoterápicos & Espécies Nativas",
        "status": "Em andamento",
        "year": 2026,
        "summary": "Startup voltada a soluções com espécies nativas da Amazônia.",
        "problem": "",
        "solution": "",
        "results": [],
        "team_names": ["Marta Adelino", "José Luiz Bezerra de Faria Filho", "Dayam Marques", "Anne Grace", "Roberta de Freitas Lopes"],
        "startup_profile": {
            "focus_area": "Fitoterápicos & Espécies Nativas",
            "species_or_subject": "Astrocaryum ulei (Murumuru)",
            "institution": "UFAC/LABTEC.IN",
        },
        "link": "",
    },
    {
        "title": "Remédio Vivo",
        "category": "Startup",
        "area": "Microverdes & Nutracêuticos",
        "status": "Em andamento",
        "year": 2026,
        "summary": "Startup dedicada ao estudo de microverdes e nutracêuticos.",
        "problem": "",
        "solution": "",
        "results": [],
        "team_names": ["Dayam Marques", "Anne Grace", "Marta Adelino"],
        "startup_profile": {
            "focus_area": "Microverdes & Nutracêuticos",
            "species_or_subject": "",
            "institution": "UFAC/LABTEC.IN",
        },
        "link": "",
    },
    {
        "title": "Amazon Green Line",
        "category": "Startup",
        "area": "PANC",
        "status": "Em andamento",
        "year": 2026,
        "summary": "Startup de pesquisa e inovação com plantas alimentícias não convencionais.",
        "problem": "",
        "solution": "",
        "results": [],
        "team_names": ["Marilene Lima", "Almecina Balbino", "Matheus Matos do Nascimento", "Marta Adelino"],
        "startup_profile": {
            "focus_area": "PANC",
            "species_or_subject": "Alternanthera sessilis (Espinafre brasileiro)",
            "institution": "UFAC/LABTEC.IN",
        },
        "link": "",
    },
]

RESEARCH_PROJECTS = [
    {
        "title": "Pesquisa de Bioativos da Amazônia",
        "slug": "pesquisa-de-bioativos-da-amazonia",
        "summary": "Estudo dos compostos bioativos presentes em espécies amazônicas.",
        "project_status": ResearchProject.ProjectStatus.IN_PROGRESS,
        "team": [1, 3],
    },
]

POSTS = [
    {
        "unit_slug": "labtec-in",
        "title": "Coordenadora da LABTEC.IN é premiada por inovação tecnológica",
        "slug": "coordenadora-da-latec-e-premiada-por-inovacao-tecnologica",
        "date": "2026-05-29",
        "summary": "A professora Marta Adelino da Silva recebeu uma moção honrosa por sua contribuição à inovação e à biodiversidade amazônica.",
        "content": "A professora Marta Adelino da Silva, do Centro de Ciências da Saúde e do Desporto da Ufac, recebeu, em 29 de maio, o Prêmio Artur Parreira: Moção Honrosa Mérito Científico do Continente Americano. Ela foi certificada pela apresentação do artigo “Inovação e Biodiversidade Amazônica: Do Empreendedorismo Sustentável à Inovação Tecnológica”, do qual é coautora, na 5ª edição dos Congressos Brasileiro e Internacional de Educação Empreendedora, Sustentabilidade e Inovação, ocorridos no Rio de Janeiro.\n\nMarta liderou a equipe premiada, composta pelos pesquisadores Roberta de Freitas Lopes, José Luiz Bezerra de Faria Filho, Anne Grace Andrade da Cunha Marques e Dayan Marques. Ela possui uma trajetória acadêmica marcada pelo pioneirismo em inovação com nanotecnologia de fármacos; também desenvolveu sua pesquisa de doutorado em biotecnologia e biodiversidade, defendida na Ufac por meio do programa de pós-graduação da Rede Bionorte.\n\nAlém disso, a pesquisadora e farmacêutica integra a Pró-Reitoria de Inovação e Tecnologia da Ufac e a startup Farma Amazônia, fundamentada na valorização da bioeconomia regional.",
        "cover_image": "news/premioMarta.png",
        "body_image": "news/certificado.png",
        "links": [
            {
                "label": "5ª edição dos Congressos Brasileiro e Internacional de Educação Empreendedora, Sustentabilidade e Inovação",
                "url": "https://cbae.ufrj.br/2026/05/25/5-congresso-brasileiro-de-educacao-empreendedora-sustentabilidade-e-inovacao/",
            },
        ],
    },
    {
        "unit_slug": "latec",
        "title": "LATEC participa do congresso nacional de inovação",
        "slug": "latec-participa-do-congresso-nacional-de-inovacao",
        "date": "2026-05-15",
        "summary": "A LATEC apresentou três projetos no congresso nacional, recebendo destaque na sessão de biotecnologia.",
        "content": "No congresso nacional de inovação tecnológica, a LATEC foi representada pelos projetos “Fábrica de Ensino”, “Pesquisa de Bioativos da Amazônia” e “Extensão em Tecnologias Sustentáveis”. As apresentações foram bem recebidas e destacaram o potencial dos alunos da UFAC.",
        "cover_image": "",
        "body_image": "",
    },
    {
        "unit_slug": "labtec-in",
        "title": "Professora do LABTEC.IN recebe o título de Dama Comendadora por trajetória acadêmica em nutrição",
        "slug": "professora-do-labtec-in-e-homenageada-por-trajetoria-na-nutricao",
        "date": "2026-06-26",
        "summary": "Bruna da Costa Viana Oliveira recebeu a Ordem do Mérito Acadêmico e Profissional, com ênfase em Nutrição, no grau de Dama Comendadora.",
        "content": "A professora do curso de Nutrição da Ufac, Bruna da Costa Viana Oliveira, recebeu a Ordem do Mérito Acadêmico e Profissional, com ênfase em Nutrição, no grau de Dama Comendadora. A homenagem foi concedida pela Câmara Brasileira de Cultura, em 26 de junho, em reconhecimento à trajetória profissional e às contribuições da professora para educação, ciência, cultura e desenvolvimento da sociedade.\n\nBruna é acreana, graduada em Nutrição pela Universidade Federal da Paraíba e atua nas áreas de ensino, pesquisa e extensão. Ao longo da carreira acadêmica, desenvolve atividades voltadas à formação de estudantes e à produção científica.\n\n“Quando ouvi meu nome, compreendi que aquela honraria não me tornava melhor do que ninguém”, disse Bruna. “Ela me lembrava da responsabilidade de honrar cada oportunidade que recebi e de continuar buscando ser uma versão melhor de mim mesma.”\n\nBruna também destacou que a comenda reforça seu compromisso com a educação e a formação de novos profissionais. “Ao deixar aquele palco, levei comigo mais do que uma comenda; levei a certeza de que a educação continua sendo a força capaz de transformar destinos, como transformou o meu, e de que esse reconhecimento só faz sentido quando nos inspira a servir ainda mais.”",
        "cover_image": "news/premioBruna.png",
        "body_image": "",
    },
    {
        "unit_slug": "labtec-in",
        "title": "Estagiário do LABTEC.IN participará de fórum sobre internet no Quênia",
        "slug": "estagiario-do-labtec-in-participara-de-forum-sobre-internet-no-quenia",
        "date": "2026-07-30",
        "summary": "Gabriel Daniel da Silva foi selecionado para participar do Fórum de Governança da Internet, em Nairobi.",
        "content": "O estudante Gabriel Daniel da Silva, do 7º período do curso de Sistemas de Informação da Ufac, foi um dos dez selecionados para participar da 21ª reunião anual do Fórum de Governança da Internet (IGF, na sigla em inglês), evento organizado pela Organização das Nações Unidas, que ocorrerá de 14 a 18 de dezembro, em Nairobi, no Quênia.\n\n“Me sinto muito feliz e realizado por essa conquista. Ser o único acreano selecionado nesta edição é motivo de grande orgulho”, disse Gabriel. “Precisamos, sim, discutir a internet; mas, antes de tudo, precisamos garantir que todas as pessoas tenham acesso a ela.”\n\nEle foi um dos participantes do programa Youth Brasil-2026, realizado durante o 16º Fórum da Internet no Brasil, ocorrido de 25 a 29 de maio, no Hangar Convenções & Feiras da Amazônia, em Belém, e promovido pelo Comitê Gestor da Internet no Brasil e pelo Núcleo de Informação e Coordenação do Ponto BR.\n\nO programa reúne jovens de todo o país para debater temas relacionados à governança da internet e ao futuro do ambiente digital. Entre os 25 participantes selecionados para a edição deste ano, dez foram escolhidos para representar o grupo no Fórum de Governança da Internet da América Latina e Caribe e cinco no Fórum Lusófono da Internet.",
        "cover_image": "people/gabriel.png",
        "body_image": "",
        "links": [
            {"label": "21ª reunião anual do Fórum de Governança da Internet", "url": "https://intgovforum.org/en/dashboard/igf-2026"},
            {"label": "programa Youth Brasil-2026", "url": "https://fib.cgi.br/pt/youth"},
            {"label": "Comitê Gestor da Internet no Brasil", "url": "https://cgi.br/"},
            {"label": "Núcleo de Informação e Coordenação do Ponto BR", "url": "https://nic.br/"},
        ],
    },
]

COURSES = [
    {
        "title": "Nanotecnologias de cosméticos",
        "description": "Aprenda sobre as aplicações de nanotecnologia na indústria cosmética.",
        "date": "2026-07-10",
        "enrollment_status": Course.EnrollmentStatus.OPEN,
        "materials": ["Apostila Nanotecnologia.pdf"],
        "link": "",
    },
    {
        "title": "Workshop de ML em Biotecnologia",
        "description": "Fundamentos de IA e Machine Learning aplicados à biotecnologia.",
        "date": "2026-08-15",
        "enrollment_status": Course.EnrollmentStatus.COMING_SOON,
        "materials": [],
        "link": "",
    },
]

MATERIALS = {
    "Apostila Nanotecnologia.pdf": {
        "title": "Apostila de Nanotecnologia",
        "description": "Apostila utilizada no curso de Nanotecnologia da LATEC.",
        "file": "course-materials/Apostila Nanotecnologia.pdf",
    }
}

class Command(BaseCommand):
    help = "Inicializa uma base vazia com o conteúdo canônico do portal."

    def handle(self, *args, **options):
        if InstitutionalUnit.objects.filter(slug="labtec-in").exists():
            raise CommandError(
                "A base já foi inicializada. Depois do bootstrap, altere o conteúdo pelo Django Admin."
            )
        self.validate_seed_assets()
        self.person_by_source_id = {}
        self.membership_role_by_source_id = {}
        self.startup_people = {}
        with transaction.atomic():
            self.seed_institutional_units()
            self.seed_people()
            self.seed_institution_memberships()
            self.seed_axes()
            self.seed_axis_mentorships()
            self.seed_mentor_memberships()
            self.seed_project_categories()
            self.seed_project_statuses()
            self.seed_projects()
            self.seed_research_projects()
            self.seed_posts()
            self.seed_courses()
            self.seed_metrics()
            self.seed_site_settings()
        self.stdout.write(self.style.SUCCESS("Seed inicial concluído."))

    def seed_institutional_units(self):
        self.labtec_unit, _created = InstitutionalUnit.objects.update_or_create(
            slug="labtec-in",
            defaults={
                "name": "LABTEC.IN",
                "acronym": "LABTEC.IN",
                "unit_type": InstitutionalUnit.UnitType.LABORATORY,
                "parent": None,
                "description": "Laboratório de Biotecnologia, Biodiversidade e Inovação.",
                "display_order": 1,
            },
        )
        self.latec_unit, _created = InstitutionalUnit.objects.update_or_create(
            slug="latec",
            defaults={
                "name": "LATEC",
                "acronym": "LATEC",
                "unit_type": InstitutionalUnit.UnitType.ACADEMIC_LEAGUE,
                "parent": self.labtec_unit,
                "description": "A LATEC é a Liga Acadêmica de Biotecnologia, Biodiversidade e Inovação da UFAC. Vinculada ao LABTEC.IN, reúne estudantes e docentes de diferentes áreas para desenvolver atividades de ensino, pesquisa e extensão voltadas à valorização da biodiversidade amazônica, à formação científica e à criação de produtos, processos e soluções inovadoras com impacto social e regional.",
                "display_order": 2,
            },
        )

    def seed_people(self):
        for order, (source_id, name, role_name, bio, photo_path) in enumerate(PEOPLE, start=1):
            person, _created = Person.objects.update_or_create(
                slug=slugify(name),
                defaults={
                    "full_name": name,
                    "short_bio": bio,
                    "is_active": True,
                    "display_order": order,
                },
            )
            self.attach_local_file(person, "photo", photo_path)
            self.person_by_source_id[source_id] = person
            self.membership_role_by_source_id[source_id] = role_name
        for order, name in enumerate(STARTUP_PEOPLE, start=len(PEOPLE) + 1):
            person, _created = Person.objects.update_or_create(
                slug=slugify(name),
                defaults={"full_name": name, "is_active": True, "display_order": order},
            )
            self.startup_people[name] = person

    def seed_institution_memberships(self):
        units_by_role = {
            "Coordenadora": (self.labtec_unit, self.latec_unit),
            "Estagiário": (self.labtec_unit,),
            "Ligante": (self.latec_unit,),
            "Pesquisador": (self.labtec_unit,),
            "Professor": (self.labtec_unit,),
        }
        for source_id, person in self.person_by_source_id.items():
            role_name = self.membership_role_by_source_id[source_id]
            for unit in units_by_role.get(role_name, ()):
                InstitutionMembership.objects.get_or_create(
                    person=person,
                    unit=unit,
                    role=role_name,
                    defaults={
                        "is_active": True,
                        "is_public": True,
                        "display_order": person.display_order,
                    },
                )

    def seed_axes(self):
        axes = [
            (1, "Etnobotânica e Pós-Colheita", "Cultivo, manejo e óleos essenciais.", "etnobotânica,pós-colheita,óleos essenciais"),
            (2, "Práticas em Laboratório e Nanotecnologia", "Farmácia Viva, farmacologia aplicada a plantas medicinais e fitoquímica.", "laboratório,nanotecnologia,fitoquímica,farmácia viva"),
            (3, "Nutrição e Ciências dos Alimentos", "Educação Alimentar, desenvolvimento e avaliação de alimentos, interface clínica e eventos Científicos.", "nutrição,ciências dos alimentos,educação alimentar,eventos científicos"),
            (4, "Saúde e bem-estar", "Produção de ativos para aplicação em saúde integrativa.", "saúde,bem-estar,saúde integrativa"),
            (5, "Produção Vegetal e Biotecnologia", "Produção vegetal, biotecnologia de plantas, fitotecnia, genética vegetal, horticultura, manejo de culturas, PANCs", "produção vegetal,biotecnologia,fitotecnia,genética vegetal,horticultura,pancs"),
            (6, "Agroindustrialização", "Desenvolvimento de produtos, processamento de matérias-primas amazônicas, inovação tecnológica", "agroindustrialização,produtos amazônicos,inovação tecnológica"),
            (7, "Redação Científica", "Produção acadêmica, escrita de artigos, resumos, projetos, revisão de literatura", "redação científica,artigos,resumos,projetos,revisão de literatura"),
        ]
        for number, title, description, keywords in axes:
            ResearchAxis.objects.update_or_create(
                number=number,
                defaults={
                    "unit": self.latec_unit,
                    "title": title,
                    "slug": slugify(title),
                    "description": description,
                    "keywords": keywords,
                    "is_active": True,
                    "display_order": number,
                },
            )

    def seed_axis_mentorships(self):
        mentorships = [
            (1, "Almecina Balbino"),
            (2, "Marta Adelino"),
            (3, "Bruna Viana"),
            (4, "Kleyton Passos"),
            (5, "Marilene Lima"),
            (5, "Bruno Favero"),
            (6, "Luciana Castello"),
            (7, "Dayam Marques"),
            (7, "Anne Grace"),
        ]
        for order, (axis_number, person_name) in enumerate(mentorships, start=1):
            axis = ResearchAxis.objects.get(number=axis_number)
            person = Person.objects.filter(slug=slugify(person_name)).first()
            if not person:
                continue
            AxisMentorship.objects.update_or_create(
                axis=axis,
                person=person,
                defaults={"role": "Orientador", "is_main_mentor": True, "display_order": order},
            )

    def seed_mentor_memberships(self):
        mentorships = AxisMentorship.objects.filter(axis__unit=self.latec_unit).select_related("person")
        for mentorship in mentorships:
            InstitutionMembership.objects.get_or_create(
                person=mentorship.person,
                unit=self.latec_unit,
                role="Orientador",
                defaults={
                    "is_active": True,
                    "is_public": True,
                    "display_order": mentorship.person.display_order,
                },
            )

    def seed_project_categories(self):
        categories = ["Ensino", "Extensão", "Startup", "Premiação"]
        for order, name in enumerate(categories, start=1):
            ProjectCategory.objects.update_or_create(
                slug=slugify(name),
                defaults={"name": name, "is_active": True, "display_order": order},
            )

    def seed_project_statuses(self):
        statuses = ["Planejado", "Em andamento", "Concluído", "Arquivado"]
        for order, name in enumerate(statuses, start=1):
            ProjectStatus.objects.update_or_create(
                slug=slugify(name),
                defaults={"name": name, "display_order": order},
            )

    def seed_projects(self):
        for item in PROJECTS:
            project_defaults = {
                "title": item["title"],
                "category": ProjectCategory.objects.get(slug=slugify(item["category"])),
                "area": item["area"],
                "status": ProjectStatus.objects.get(slug=slugify(item["status"])),
                "year": item["year"],
                "summary": item["summary"],
                "problem": item["problem"],
                "solution": item["solution"],
            }
            project, _created = Project.objects.update_or_create(
                slug=slugify(item["title"]),
                defaults=project_defaults,
                create_defaults={
                    **project_defaults,
                    "unit": self.latec_unit,
                    "editorial_status": EditorialStatus.PUBLISHED,
                    "published_at": self.datetime_from_date(date(item["year"], 1, 1)),
                },
            )
            # Classificação provisória: estes registros vieram do protótipo
            # histórico da Liga e ainda aguardam revisão institucional manual.
            for result_order, result_title in enumerate(item["results"], start=1):
                ProjectResult.objects.update_or_create(
                    project=project,
                    title=result_title,
                    defaults={"description": "", "display_order": result_order},
                )
            for member_order, source_id in enumerate(item.get("team", []), start=1):
                person = self.person_by_source_id.get(source_id)
                if not person:
                    continue
                ProjectTeamMember.objects.update_or_create(
                    project=project,
                    person=person,
                    defaults={"role": "Equipe", "is_lead": member_order == 1, "display_order": member_order},
                )
            for member_order, name in enumerate(item.get("team_names", []), start=1):
                person = self.startup_people.get(name) or Person.objects.filter(slug=slugify(name)).first()
                if person:
                    ProjectTeamMember.objects.update_or_create(
                        project=project,
                        person=person,
                        defaults={"role": "Equipe", "is_lead": member_order == 1, "display_order": member_order},
                    )
            if item.get("startup_profile"):
                ProjectStartupProfile.objects.update_or_create(
                    project=project,
                    defaults=item["startup_profile"],
                )
            if item["link"]:
                ProjectLink.objects.update_or_create(
                    project=project,
                    url=item["link"],
                    defaults={"label": "Link externo", "link_type": "externo", "display_order": 1},
                )

    def seed_research_projects(self):
        for item in RESEARCH_PROJECTS:
            research_project, _created = ResearchProject.objects.get_or_create(
                slug=item["slug"],
                defaults={
                    "unit": self.latec_unit,
                    "title": item["title"],
                    "summary": item["summary"],
                    "project_status": item["project_status"],
                    "editorial_status": EditorialStatus.PUBLISHED,
                    "published_at": self.datetime_from_date(date(2026, 1, 1)),
                },
            )
            for member_order, source_id in enumerate(item["team"], start=1):
                person = self.person_by_source_id.get(source_id)
                if not person:
                    continue
                ResearchProjectMember.objects.get_or_create(
                    research_project=research_project,
                    person=person,
                    defaults={
                        "role": (
                            ResearchProjectMember.Role.COORDINATOR
                            if member_order == 1
                            else ResearchProjectMember.Role.COLLABORATOR
                        ),
                        "display_order": member_order,
                    },
                )

    def seed_posts(self):
        for item in POSTS:
            published_at = self.datetime_from_iso_date(item["date"])
            post_defaults = {
                "unit": InstitutionalUnit.objects.get(slug=item["unit_slug"]),
                "title": item["title"],
                "summary": item["summary"],
                "content": item["content"],
            }
            post, _created = Post.objects.update_or_create(
                slug=item["slug"],
                defaults=post_defaults,
                create_defaults={
                    **post_defaults,
                    "editorial_status": EditorialStatus.PUBLISHED,
                    "published_at": published_at,
                },
            )
            self.attach_local_file(post, "cover_image", item["cover_image"])
            self.attach_local_file(post, "body_image", item["body_image"])
            for order, link in enumerate(item.get("links", []), start=1):
                PostLink.objects.update_or_create(
                    post=post,
                    url=link["url"],
                    defaults={"label": link["label"], "display_order": order},
                )

    def seed_courses(self):
        for item in COURSES:
            course_defaults = {
                "unit": self.latec_unit,
                "title": item["title"],
                "description": item["description"],
                "start_date": date.fromisoformat(item["date"]),
                "enrollment_status": item["enrollment_status"],
                "registration_url": item["link"],
            }
            course, _created = Course.objects.update_or_create(
                slug=slugify(item["title"]),
                defaults=course_defaults,
                create_defaults={
                    **course_defaults,
                    "editorial_status": EditorialStatus.PUBLISHED,
                    "published_at": self.datetime_from_iso_date(item["date"]),
                },
            )
            for material_order, material_name in enumerate(item["materials"], start=1):
                material_data = MATERIALS.get(material_name, {"title": material_name, "description": "", "file": ""})
                material, _created = CourseMaterial.objects.update_or_create(
                    course=course,
                    title=material_data["title"],
                    defaults={
                        "description": material_data["description"],
                        "display_order": material_order,
                    },
                )
                self.attach_local_file(material, "file", material_data["file"])

    def seed_metrics(self):
        metrics = [
            ("membros", "Membros", 33),
            ("projetos", "Projetos", 20),
            ("publicacoes", "Artigos e publicações", 12),
            ("parcerias", "Parcerias", 5),
            ("cursos", "Cursos", 2),
            ("premiacoes", "Premiações", 1),
        ]
        for order, (key, label, value) in enumerate(metrics, start=1):
            ImpactMetric.objects.update_or_create(
                key=key,
                defaults={
                    "unit": self.labtec_unit,
                    "label": label,
                    "value": value,
                    "is_active": True,
                    "display_order": order,
                },
            )

    def seed_site_settings(self):
        site_settings = SiteSettings.objects.filter(unit=self.labtec_unit).order_by("id").first() or SiteSettings()
        site_settings.unit = self.labtec_unit
        site_settings.site_name = "LABTEC.IN"
        site_settings.institution = "Laboratório de Biotecnologia, Biodiversidade e Inovação"
        site_settings.is_active = True
        if not site_settings.description:
            site_settings.description = "Portal institucional do LABTEC.IN."
        site_settings.save()

        HeroBanner.objects.update_or_create(
            title="Biotecnologia, biodiversidade e inovação",
            defaults={
                "unit": self.labtec_unit,
                "subtitle": "Um laboratório conectando ensino, pesquisa e extensão para transformar ciência em soluções para a Amazônia.",
                "cta_label": "Conheça os projetos",
                "cta_url": "#portfolio",
                "is_published": True,
                "display_order": 1,
            },
        )
        sections = [
            ("mission", "Missão", "Desenvolver soluções tecnológicas e científicas para a Amazônia, promovendo formação acadêmica e impacto social."),
            ("vision", "Visão", "Tornar-se referência nacional em inovação biotecnológica e proteção da biodiversidade amazônica."),
            ("values", "Valores", "Ética, inovação, sustentabilidade, colaboração e excelência."),
        ]
        for order, (section_type, title, content) in enumerate(sections, start=1):
            InstitutionalSection.objects.update_or_create(
                slug=slugify(title),
                defaults={
                    "unit": self.labtec_unit,
                    "section_type": section_type,
                    "title": title,
                    "content": content,
                    "is_published": True,
                    "display_order": order,
                },
            )

    def attach_local_file(self, instance, field_name, source_relative_path):
        if not source_relative_path:
            return
        source_path = self.seed_asset_path(source_relative_path)

        field_file = getattr(instance, field_name)
        model_field = instance._meta.get_field(field_name)
        generated_name = model_field.generate_filename(instance, source_path.name)
        previous_name = field_file.name
        if previous_name == generated_name and default_storage.exists(generated_name):
            return
        if default_storage.exists(generated_name):
            setattr(instance, field_name, generated_name)
            instance.save(update_fields=[field_name])
        else:
            with source_path.open("rb") as file_obj:
                field_file.save(source_path.name, File(file_obj), save=True)
        if previous_name and previous_name != getattr(instance, field_name).name and default_storage.exists(previous_name):
            default_storage.delete(previous_name)

    def seed_asset_path(self, source_relative_path):
        root = Path(getattr(settings, "SEED_ASSETS_ROOT", settings.BASE_DIR / "seed_assets"))
        return root / source_relative_path

    def validate_seed_assets(self):
        required_assets = {
            photo_path for *_person, photo_path in PEOPLE
        }
        required_assets.update(
            path
            for post in POSTS
            for path in (post["cover_image"], post["body_image"])
            if path
        )
        required_assets.update(item["file"] for item in MATERIALS.values() if item["file"])
        missing = sorted(path for path in required_assets if not self.seed_asset_path(path).is_file())
        if missing:
            raise CommandError("Ativos canônicos ausentes: " + ", ".join(missing))

    def datetime_from_iso_date(self, value):
        return self.datetime_from_date(date.fromisoformat(value))

    def datetime_from_date(self, value):
        return timezone.make_aware(datetime.combine(value, time.min))

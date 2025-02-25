from os import path
from os import remove
import random
import base64


n_tecnologias=0

def random_tecnologias():
    n_t = random.randint(1, n_tecnologias)
    tech = []
    cont = 0

    while cont < n_t:
        random_technologias = random.randint(1, n_tecnologias)
        tecnologias_id = "technology_"+str(random_technologias)
        if not tecnologias_id in tech:
            tech.append(tecnologias_id)
            cont += 1
    return tech

def format_random_tecnologias():
    tech=random_tecnologias()

    tech_string="[(6,0,["
    for i in range(len(tech)):
        tech_string += "ref(\'"+tech[i]+"\')"
        if i <len(tech)-1:
            tech_string+=","
    tech_string+="])]"
    return tech_string


def borrar_fichero(file):
     if path.exists(file):
          remove(file)

def escribir_texto(text, file):
    with open(file, 'a') as f:
        f.write(text)

def escribir_desarrollador(linea, demo_file):
    escribir_texto(f'<record id=\'dev_{linea[0]}\' model=\'res.partner\'>', demo_file)
    escribir_texto(f'<field name=\'name\'>{linea[1]}</field>', demo_file)
    escribir_texto(f'<field name=\'ultimo_login\' eval=\"(datetime.now().strftime(\'%Y-%m-%d\'))\"></field>', demo_file)
    escribir_texto(f'<field name=\'codigo_acceso\'>{linea[2]}</field>', demo_file)
    escribir_texto(f'<field name=\'es_desarrollador\'>True</field>', demo_file)
    escribir_texto(f'<field name=\'tecnologias\' eval=\"{format_random_tecnologias()}\"></field>', demo_file)
    escribir_texto(f'</record>', demo_file)

def escribir_proyecto(line, demo_file):
    escribir_texto(f'<record id=\'project_{line[0]}\' model=\'gestionar_proyectos_emp.proyecto\'>', demo_file)
    escribir_texto(f'<field name=\'nombre\'>{line[1]}</field>', demo_file)
    escribir_texto(f'</record>', demo_file)

def escribir_historia(line, demo_file):
    escribir_texto(f'<record id=\'history_{line[0]}\' model=\'gestionar_proyectos_emp.historias\'>', demo_file)
    escribir_texto(f'<field name=\'nombre\'>{line[1]}</field>', demo_file)

    escribir_texto(f'<field name=\'proyecto\' ref=\'project_1\'></field>', demo_file)
    escribir_texto(f'</record>', demo_file) 

def escribir_tecnologia(line, demo_file):
    escribir_texto(f'<record id=\'technology_{line[0]}\' model=\'gestionar_proyectos_emp.tecno\'>', demo_file)
    escribir_texto(f'<field name=\'nombre\'>{line[1]}</field>', demo_file)

    image = open("tech_images/"+line[1].strip()+".png", "rb")
    b64_string = base64.b64encode(image.read()).decode('utf_8')
    
    escribir_texto(f'<field name=\'foto\'>{b64_string}</field>', demo_file)
    escribir_texto(f'</record>', demo_file)




def generador_desarroladores(source, demo_file):
    borrar_fichero(demo_file)
    escribir_texto('<odoo><data>', demo_file)
    with open(source) as file:

        for line in file:
            line=line.split(',')
            escribir_desarrollador(line, demo_file)
    escribir_texto('</data></odoo>', demo_file)


def generador_proyectos(source, demo_file):
    borrar_fichero(demo_file)
    escribir_texto('<odoo><data>', demo_file)
    with open(source) as file:
        for line in file:
            line = line.split(',')
            escribir_proyecto(line, demo_file)
    escribir_texto('</data></odoo>', demo_file)

def generador_historias(source, demo_file):
    borrar_fichero(demo_file)
    escribir_texto('<odoo><data>', demo_file)
    with open(source) as file:
        for line in file:
            line = line.split(',')
            escribir_historia(line, demo_file)
    escribir_texto('</data></odoo>', demo_file)

def generador_tecnologias(source, demo_file):
    global n_tecnologias
    borrar_fichero(demo_file)
    escribir_texto('<odoo><data>', demo_file)
    with open(source) as file:
        for line in file:
            line = line.split(',')
            n_tecnologias=n_tecnologias+1
            escribir_tecnologia(line, demo_file)

    escribir_texto('</data></odoo>', demo_file)


generador_tecnologias('CSV/tecnologias.csv', 'demo/tecnologias.xml')
generador_desarroladores('CSV/desarrolladores.csv', 'demo/desarrolladores.xml')
generador_proyectos('CSV/proyectos.csv', 'demo/proyectos.xml')
generador_historias('CSV/historias.csv', 'demo/historias.xml')


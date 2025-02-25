# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import _
import datetime
import logging
import re

_logger = logging.getLogger(__name__) #Informacion que obtiene del fichero de configuracion

class desarrollador(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    
    ultimo_login = fields.Date()

    es_desarrollador=fields.Boolean()

    codigo_acceso=fields.Char()

    tecnologias = fields.Many2many('gestionar_proyectos_emp.tecno',
                                    relation='tecnologias_desarrollador',
                                    column1='desarrollador_id',
                                    column2='tecnologias_id')
    
    tareas = fields.Many2many('g_p_emp.tarea',
                                    relation='tareas_desarrollador',
                                    column1='desarrollador_id',
                                    column2='tareas_id')
    
    bugs = fields.Many2many('g_p_emp.bug',
                                    relation='bugs_desarrollador',
                                    column1='desarrollador_id',
                                    column2='bug_id')
    
    mejoras = fields.Many2many('g_p_emp.mejora',
                                    relation='mejoras_desarrollador',
                                    column1='desarrollador_id',
                                    column2='mejora_id')
    

    @api.constrains('codigo_acceso')
    def _check_code(self):
        regex =re.compile('^[0-9]{8}[a-z]',re.I)
        for dev in self:
            if regex.match(dev.codigo_acceso):
                _logger.info('Codigo de acceso generado correctamente')
            else:
                raise ValidationError('Formato de codigo de acceso incorrecto')

    _sql_constraints=[('codigo_acceso_unico','unique(codigo_acceso)','Codigo de acceso ya existe')]


    def _desarrollador_categoria(self):
        for dev in self:
            categorias=dev.env['res.partner.category'].search([('name','=','Desarrolladores')])
            if len(categorias)>0:
                categoria=categorias[0]

            else:
                categoria=dev.env['res.partner.category'].create({'name':'Desarrolladores'})
            return categoria

    
    @api.onchange('es_desarrollador')
    def _onchange_es_desarrollador(self):
        categoria=self._desarrollador_categoria()
        self.category_id=[(4,categoria.id)]


    @api.constrains('es_desarrollador')
    def _check_es_desarrollador(self):
        categoria=self._desarrollador_categoria()
        for desarrollador in self:
            if desarrollador.es_desarrollador:
                desarrollador.category_id=[(4, categoria.id)]



class proyecto (models.Model):
    _name = 'gestionar_proyectos_emp.proyecto' 
    _description = 'gestionar_proyectos_emp.proyecto'
    
    nombre = fields.Char()
    descripcion=fields.Text()
    historias = fields.One2many(comodel_name="gestionar_proyectos_emp.historias", inverse_name="proyecto")
    
    

class historiasdeusuario (models.Model):
    _name = 'gestionar_proyectos_emp.historias' 
    _description = 'gestionar_proyectos_emp.historias'
    
    nombre = fields.Char()
    descripcion=fields.Text()
    proyecto = fields.Many2one("gestionar_proyectos_emp.proyecto", ondelete="set null")
    tareas=fields.One2many(string="Tareas", comodel_name="g_p_emp.tarea", inverse_name="historia")
    tecnologias_usadas = fields.Many2many("gestionar_proyectos_emp.tecno", compute="_obtener_tecnologias_usadas")
    
    
    def _obtener_tecnologias_usadas(self):
        for historias in self:
            tecnologias = None
            for tarea in historias.tareas:
                if not tecnologias:
                    tecnologias=gestionar_proyectos_emp.tecno
                else:
                    tecnologias = tecnologias + gestionar_proyectos_emp.tecno
            historias.tecnologias_usadas = tecnologias


class tarea(models.Model):
    _name = 'g_p_emp.tarea'
    _description = 'tarea'

    fecha_definicion= fields.Datetime(default=lambda d: datetime.datetime.now())
    proyecto = fields.Many2one('gestionar_proyectos_emp.proyecto', related='historia.proyecto', readonly=True)
    codigo =fields.Char(compute="_obtener_codigo")
    nombre = fields.Char(string="Nombre", readonly=False, required=True, help="Introduzca el nombre")
    historia = fields.Many2one("gestionar_proyectos_emp.historias", ondelete="set null", help="Historia relacionada")
    descripcion=fields.Text()
    fecha_inicio=fields.Datetime()
    fecha_fin=fields.Datetime()
    esta_pausada=fields.Boolean()
    sprint=fields.Many2one("gestionar_proyectos_emp.sprint", compute="_obtener_sprint", store=True)
    tecnologia= fields.Many2many(comodel_name="gestionar_proyectos_emp.tecno",
                                relation_name="tareas_tecno",
                                column1="tarea_id",
                                column2="tecnologia_id")
    desarrolladores =fields.Many2many('res.partner')
           

    def _obtener_codigo(self):
        for tarea in self:
            try:
                tarea.codigo = "TSK_"+str(tarea.id)
                _logger.debug("Codigo generado: "+tarea.codigo)
            except:
                raise ValidationError(_("Generacion de codigo erronea"))
    
    
    @api.depends('codigo')
    def _obtener_sprint(self):
        for tarea in self:
           # sprints = self.env['gestionar_proyectos_emp.sprint'].search([('proyecto.id', '=',tarea.historia.proyecto.id)])
            if isinstance(tarea.historia.proyecto.id, models.NewId):
                id_proyecto=int(tarea.historia.proyecto.id.origin)
            else:
                id_proyecto=tarea.historia.proyecto.id
            sprints = self.env['gestionar_proyectos_emp.sprint'].search([('proyecto.id', '=',id_proyecto)])

            found = False
            for sprint in sprints: 
                if isinstance(sprint.fecha_fin, datetime.datetime) and sprint.fecha_fin > datetime.datetime.now():
                    tarea.sprint=sprint.id
                    found = True
            if not found:
                tarea.sprint = False
    
    def _obtener_desarrollador_por_defecto(self):
        dev =self.browse(self._context.get('current_developer'))
        if dev:
            return [dev.id]
        else:
            return[]
        
    desarrolladores = fields.Many2many(comodel_name='res.partner',
                                  relation='desarrolladores_tarea',
                                  column1='id_tarea',
                                  column2='id_desarrolador',
                                  default=_obtener_desarrollador_por_defecto)

class bug(models.Model):
    _name = 'g_p_emp.bug'
    _description = 'g_p_emp.bug'
    _inherit='g_p_emp.tarea'

    tecnologias= fields.Many2many(comodel_name="gestionar_proyectos_emp.tecno",
                                relation="bugs_tecnologia_rel",
                                column1="bug_id",
                                column2="tecnologia_id")
    
    tareas_enlazadas= fields.Many2many(comodel_name="g_p_emp.tarea",
                                relation="tareas_bugs",
                                column1="id_bug",
                                column2="id_tarea")

    bugs_enlazados= fields.Many2many(comodel_name="g_p_emp.bug",
                                relation="bugs_bugs",
                                column1="id_bug1",
                                column2="id_bug2") 

    mejoras_enlazadas= fields.Many2many(comodel_name="g_p_emp.mejora",
                                relation="mejora_bugs",
                                column1="id_bug",
                                column2="id_mejora")      
           
    desarrolladores= fields.Many2many(comodel_name="res.partner",
                                relation="desarrolladores_bugs",
                                column1="id_bug",
                                column2="id_desarrollador")   
    

class mejora(models.Model):
    _name = 'g_p_emp.mejora'
    _description = 'g_p_emp.mejora'
    _inherit='g_p_emp.tarea'

    tecnologias= fields.Many2many(comodel_name="gestionar_proyectos_emp.tecno",
                                relation="mejoras_tecno",
                                column1="id_mejora",
                                column2="id_tecnologia")

    historiasdeusuario_relacionadas = fields.Many2many('gestionar_proyectos_emp.historias')
          
    desarrolladores= fields.Many2many(comodel_name="res.partner",
                                relation="desarrolladores_mejora",
                                column1="id_mejora",
                                column2="id_desarrollador")  


class sprint(models.Model):
    _name = 'gestionar_proyectos_emp.sprint' 
    _description = 'gestionar_proyectos_emp.sprint'

    proyecto= fields.Many2one("gestionar_proyectos_emp.proyecto")
    nombre = fields.Char()
    descripcion=fields.Text()
    duracion = fields.Integer(default=15)
    fecha_inicio=fields.Datetime()
    fecha_fin=fields.Datetime(compute="_obtener_fecha_fin", store=True)
    tarea = fields.One2many(string="Tareas", comodel_name="g_p_emp.tarea", inverse_name='sprint')
    activo = fields.Boolean(compute="_obtener_activo")


    @api.depends('fecha_inicio', 'duracion')
    def _obtener_fecha_fin(self):
        for sprint in self:
            if isinstance(sprint.fecha_inicio, datetime.datetime) and sprint.duracion>0:
                sprint.fecha_fin = sprint.fecha_inicio + datetime.timedelta(days=sprint.duracion)
            else:
                sprint.fecha_fin = sprint.fecha_inicio

    @api.depends('fecha_inicio','duracion')
    def _obtener_activo(self):
        for sprint in self:
            if (isinstance(sprint.fecha_inicio, datetime.datetime)
                and isinstance(sprint.fecha_fin, datetime.datetime)
                and sprint.fecha_fin > datetime.datetime.now()
                and sprint.fecha_inicio <= datetime.datetime.now()):
                sprint.activo = True
            else:
                sprint.activo = False      
            

class tecno(models.Model):
    _name = 'gestionar_proyectos_emp.tecno' 
    _description = 'gestionar_proyectos_emp.tecno'
    
    nombre = fields.Char()
    descripcion=fields.Text()
    
    foto = fields.Image(max_width=200, max_height=200)
    tarea = fields.Many2many(comodel_name="g_p_emp.tarea",
                            relation="tecnologia_gestionar_proyectos_emp",
                            column1="id_tecnologia",
                            column2="id_tarea")

# -*- coding: utf-8 -*-
# from odoo import http


# class GestionarProyectosEmp(http.Controller):
#     @http.route('/gestionar_proyectos_emp/gestionar_proyectos_emp', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/gestionar_proyectos_emp/gestionar_proyectos_emp/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('gestionar_proyectos_emp.listing', {
#             'root': '/gestionar_proyectos_emp/gestionar_proyectos_emp',
#             'objects': http.request.env['gestionar_proyectos_emp.gestionar_proyectos_emp'].search([]),
#         })

#     @http.route('/gestionar_proyectos_emp/gestionar_proyectos_emp/objects/<model("gestionar_proyectos_emp.gestionar_proyectos_emp"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('gestionar_proyectos_emp.object', {
#             'object': obj
#         })

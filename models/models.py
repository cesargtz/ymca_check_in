# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import json

class ymca_chek_in(models.Model):
    _name = 'ymca.chek_in'

    user_zkteco = fields.Integer()
    user_id = fields.Many2one('res.partner', compute="_get_partner", store=False)
    check_in = fields.Datetime()

    @api.depends("user_zkteco")
    def _get_partner(self):
        for check in self:
            if check.user_zkteco:
                user = check.env['partner_ymca_code'].search([('code', '=', check.user_zkteco)])
                if (user):
                    check.user_id = user.partner


class ymca_voucher_zkteck(models.Model):
    _inherit = "account.voucher"

    check_in = fields.Datetime(compute="_get_zk_record", string="Ultimo ingreso")

    @api.onchange('partner_id')
    def _get_zk_record(self):
        for rec in self:
            zk_id = rec.env['partner_ymca_code'].search([('partner', '=', rec.partner_id.id)]).code
            rec.check_in = rec.env['ymca.chek_in'].search([('user_zkteco', '=', zk_id)], order="id desc", limit=1).check_in


# class create_user_zkteco(models.Model):
#     _inherit = 'partner_ymca_code'

    # create_user = fields.Boolean(string="Crear usuario en checador", default=False)
    # name_show = fields.Char(string="Nombre a mostrar")
    # finger = fields.Integer(string="Dedo enlazado")
    # estado = fields.Char(string="Estado", default="Sin Enlazar")

    # @api.multi
    # def create_zkteco_user(self):
    #     for rec in self:
    #         print(rec.partner)
    #         user_data = ['create', '-', str(rec.name_show), '-', str(rec.code), '-', str(rec.finger)]
    #         data = ''.join(user_data)
    #         url = 'http://nvryecora.ddns.net:4375'
    #         response = requests.post(url,data)
    #         # json_data = json.loads(response.text)
    #         if response.text == "exitoso":
    #             rec.estado = 'Enlazado'
    #         elif response.text == "error":
    #             return {
    #                 'warning': {
    #                     'title': "A occurrido un error.",
    #                     'message': "Favor de contactar con el administrador del sistema."
    #                 }
    #             }
    #
    # @api.multi
    # def delete_enroll_finger(self):
    #     for rec in self:
    #         user_data = ['delFinger', '-',  str(rec.code), '-', "12"] #codigo 12 borra el usuario
    #         data = ''.join(user_data)
    #         url = 'http://nvryecora.ddns.net:4375'
    #         print("deberia borrar")
    #         response = requests.post(url,data)
    #         print(response.text)
    #         # json_data = json.loads(response.text)
    #         if response.text == "exitoso":
    #             print("entro a exitoso")
    #             rec.estado = 'Sin Enlazar'
    #             rec.finger = 0
    #         elif response.text == "error":
    #             print("error")
    #             return {
    #                 'warning': {
    #                     'title': "A occurrido un error.",
    #                     'message': "Favor de contactar con el administrador del sistema."
    #                 }
    #             }

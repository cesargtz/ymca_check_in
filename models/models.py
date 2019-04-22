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
    state_user_zktec = fields.Char(compute="_get_state_user", store=True, readonly=True)

    @api.onchange('partner_id')
    def _get_state_user(self):
        self.state_user_zktec = self.env['partner_ymca_code'].search([('partner', '=', self.partner_id.id)]).estado


    @api.onchange('partner_id')
    def _get_zk_record(self):
        for rec in self:
            if rec.partner_id:
                zk_id = rec.env['partner_ymca_code'].search([('partner', '=', rec.partner_id.id)]).code
                rec.check_in = rec.env['ymca.chek_in'].search([('user_zkteco', '=', zk_id)], order="id desc", limit=1).check_in

    @api.multi
    def open_door(self):
        for rec in self:
            user_data = ['opendoor', '-','', '-', '', '-', '']
            data = ''.join(user_data)
            url = 'http://localhost:4375'
            response = requests.post(url,data)
            if response.text == "exitoso":
                rec.estado = 'Enlazado'
            elif response.text == "error":
                return {
                    'warning': {
                        'title': "A occurrido un error.",
                        'message': "Favor de contactar con el administrador del sistema."
                    }
                }

    @api.multi
    def enable_user(self):
        if self.packages == 'f':
            res = self.enabled_user_zkteco(self.code_clock)
            if res == 1:
                users = self.env['res.partner'].search([('parent_id', '=', self.partner_id.id),('family_active','=',True)])
                for user in users:
                    res = self.enabled_user_zkteco(user.code)
                    if res != 1:
                        return {
                            'warning': {
                                'title': "A occurrido un error.",
                                'message': "Favor de contactar con el administrador del sistema."
                            }
                        }
            else:
                return {
                    'warning': {
                        'title': "A occurrido un error.",
                        'message': "Favor de contactar con el administrador del sistema."
                    }
                }
        else:
            res = self.enabled_user_zkteco(self.code_clock)
            if res != 1:
                return {
                    'warning': {
                        'title': "A occurrido un error.",
                        'message': "Favor de contactar con el administrador del sistema."
                    }
                }


    def enabled_user_zkteco(code):
        user_data = ['enabled', '-',  str(code), '-', '']
        data = ''.join(user_data)
        url = 'http://localhost:4375'
        response = requests.post(url,data)
        if response.text == "exitoso":
            return 1
        else:
            return 0

class create_user_zkteco(models.Model):
    _inherit = 'partner_ymca_code'

    create_user = fields.Boolean(string="Crear usuario en checador", default=False)
    name_show = fields.Char(string="Nombre a mostrar")
    finger = fields.Integer(string="Dedo enlazado", default=5)
    template_finger = fields.Char()
    estado = fields.Char(string="Estado", default="Sin Enlazar")

    @api.multi
    def create_zkteco_user(self):
        for rec in self:
            print(rec.partner)
            user_data = ['create', '-', str(rec.name_show), '-', str(rec.code), '-', str(rec.finger)]
            data = ''.join(user_data)
            url = 'http://localhost:4375'
            response = requests.post(url,data)
            # json_data = json.loads(response.text)
            if response.text == "exitoso":
                rec.estado = 'Enlazado'
            elif response.text == "error":
                return {
                    'warning': {
                        'title': "A occurrido un error.",
                        'message': "Favor de contactar con el administrador del sistema."
                    }
                }

    @api.multi
    def delete_enroll_finger(self):
        for rec in self:
            user_data = ['delFinger', '-',  str(rec.code), '-', "12"] #codigo 12 borra el usuario
            data = ''.join(user_data)
            url = 'http://localhost:4375'
            print("deberia borrar")
            response = requests.post(url,data)
            print(response.text)
            # json_data = json.loads(response.text)
            if response.text == "exitoso":
                print("entro a exitoso")
                rec.estado = 'Sin Enlazar'
                rec.finger = 0
            elif response.text == "error":
                print("error")
                return {
                    'warning': {
                        'title': "A occurrido un error.",
                        'message': "Favor de contactar con el administrador del sistema."
                    }
                }


class HistoryResPartner(models.Model):
    _inherit='res.partner'

    check_count = fields.Integer(compute="_check_count")

    @api.multi
    def _check_count(self):
        for record in self:
            count = 0
            codezk = record.env['partner_ymca_code'].search([('partner.id','=', record.id)]).code
            print(codezk)
            for itr in record.env['ymca.chek_in'].search([('user_zkteco','=', codezk)]):
                print(itr)
                count = count + 1
            record.check_count = count


    @api.multi
    def split_receptions_tree(self):
        tree_res = self.env['ir.model.data'].get_object_reference('ymca_chek_in', 'ymca_checkin_tree_view')
        tree_id = tree_res and tree_res[1] or False
        form_res = self.env['ir.model.data'].get_object_reference('ymca_chek_in', 'ymca_checkin_form_view')
        form_id = form_res and form_res[1] or False
        codezk = self.env['partner_ymca_code'].search([('partner.id','=', self.id)]).code

        return{
            'type'          :   'ir.actions.act_window',
            'view_type'     :   'form', #Tampilan pada tabel pop-up
            'view_mode'     :   'tree,form', # Menampilkan bagian yang di pop up, tree = menampilkan tabel tree nya utk product
            'res_model'     :   'ymca.chek_in', #Menampilkan tabel yang akan di show di pop-up screen
            'target'        :   'new', # Untuk menjadikan tampilan prduct yang dipilih menjadi pop-up table tampilan baru, jika dikosongin maka tidak muncul pop-up namun muncul halaman baru.
            'views'         :   [(tree_id, 'tree'),(form_id, 'form')],
            'domain'        :   [('user_zkteco','=', codezk)] #Filter id barang yang ditampilkan
            }


class DisableUsers(models.TransientModel):
    _name = 'zkteco.disableusers'

    date_start = fields.Date(string="Fecha de Inicio")
    date_end = fields.Date(string="Fecha Final")

    @api.multi
    def set_disable_users(self):
        users = self.env['res.partner'].search([('last_month_pay', '>=', self.date_start),('last_month_pay', '<=', self.date_end)])
        print(users)
        if users:
            for user in users:
                user_zkteco = user.env['partner_ymca_code'].search([('partner.id','=', user.id)])
                print(user_zkteco.name_show)
                res = self.disableZkteco(user_zkteco.code)
                if res == 1:
                    user_zkteco.write({'estado': "Desactivado"})
                else:
                    return {
                        'warning': {
                            'title': "A occurrido un error.",
                            'message': "Favor de contactar con el administrador del sistema."
                        }
                    }

    def disableZkteco(code):
        for rec in self:
            user_data = ['disable', '-',  str(code), '-', '']
            data = ''.join(user_data)
            url = 'http://localhost:4375'
            response = requests.post(url,data)
            if response.text == "exitoso":
                return 1
            else:
                return 0

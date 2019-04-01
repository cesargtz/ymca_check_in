# -*- coding: utf-8 -*-

from odoo import models, fields, api


class UserZkId(models.Model):
    _inherit = 'res.partner'

    user_zk_id = fields.Integer("Id Usuario Checador")

    _user_zk_uniquie = [
        ('user_zk_id_unique',
         'UNIQUE (user_zk_id)',
         'El id que esta tratando de usar, ya se encuentra asignado a otro usuario')]



class ymca_chek_in(models.Model):
    _name = 'ymca.chek_in'

    user_zkteco = fields.Integer()
    user_id = fields.Many2one('res.partner', compute="_get_partner", store=False)
    check_in = fields.Datetime()

    @api.depends("user_zkteco")
    def _get_partner(self):
        if self.user_zkteco:
            user_id = self.env['res.partner'].search([('user_zk_id', '=', self.user_zkteco)])
            if (user_id):
                self.user_id = user_id.id
            else:
                self.user_id = 0

# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import fields, models


class CurrencyRate(models.Model):
    """ Extended digits on rate for serbian accounting """

    _inherit = "res.currency.rate"

    rate = fields.Float(digits=(12, 12))

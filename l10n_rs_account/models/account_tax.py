# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import fields, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    vat_legislation_mention_id = fields.Many2one(
        comodel_name="vat.legislation.mention", string="VAT Legislation Mention"
    )

# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import fields, models


class AccountTaxTemplate(models.Model):
    """Added fields used to connect deductible and
    non-deductible taxes in serbian accounting"""

    _inherit = "account.tax.template"

    account_id = fields.Many2one(comodel_name="account.account.template")
    refund_account_id = fields.Many2one(comodel_name="account.account.template")

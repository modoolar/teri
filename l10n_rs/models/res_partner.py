# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import api, fields, models


class ResPartner(models.Model):
    """ Added field on partner to determine whether the contact is in the PDV system """

    _inherit = "res.partner"

    company_registry_number = fields.Char(string="Company Registry Number")

    """ Setting Accounts on contact base on his country of origin
     and whether he had previously set accounts. """

    @api.onchange("country_id")
    def _onchange_country(self):
        company = self.env.user.company_id
        IrProperty = self.env["ir.property"]

        if self.env.company.account_fiscal_country_id.code == "RS":
            if self.country_id and self.country_id.code != "RS":
                self.property_account_receivable_id = (
                    company.account_foreign_receivable_id
                )
                self.property_account_payable_id = company.account_foreign_payable_id
            else:
                self.property_account_receivable_id = IrProperty._get(
                    "property_account_receivable_id", "res.partner"
                )
                self.property_account_payable_id = IrProperty._get(
                    "property_account_payable_id", "res.partner"
                )

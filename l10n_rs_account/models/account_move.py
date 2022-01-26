# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    turnover_date = fields.Date(default=fields.Date.today())
    turnover_place = fields.Char(default=lambda self: self.env.company.city)
    reception_date = fields.Date()
    non_deductable = fields.Boolean()
    is_company_currency = fields.Boolean(compute="_compute_is_company_currency")
    company_currency_total = fields.Float(
        string="Total RSD", compute="_compute_amount_total_rsd"
    )

    def _compute_is_company_currency(self):
        for record in self:
            record.is_company_currency = (
                self.env.company.currency_id == self.currency_id
            )

    def _compute_amount_total_rsd(self):
        for record in self:
            currency_date = record.invoice_date or fields.Date.today()
            record.company_currency_total = (
                record.currency_id._convert(
                    record.amount_total,
                    record.company_currency_id,
                    record.company_id,
                    currency_date,
                )
                if record.currency_id != record.company_currency_id
                else record.amount_total
            )

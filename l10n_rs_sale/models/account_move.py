# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    is_downpayment = fields.Boolean(
        string="Down Payment", store=True, compute="_compute_is_downpayment"
    )
    amount_untaxed_no_downpayemnt = fields.Monetary(
        string="Untaxed Amount without down payments",
        compute="_compute_amount_no_downpayment",
    )
    amount_total_no_downpayemnt = fields.Monetary(
        string="Total without down payments", compute="_compute_amount_no_downpayment"
    )

    def _get_starting_sequence(self):
        starting_sequence = super(AccountMove, self)._get_starting_sequence()
        if self.journal_id.downpayment_sequence and self.is_downpayment:
            starting_sequence = "AVR" + starting_sequence
        return starting_sequence

    def _get_last_sequence_domain(self, relaxed=False):
        where_string, param = super(AccountMove, self)._get_last_sequence_domain(
            relaxed
        )
        if (
            self.env.company.chart_template_id
            == self.env.ref("l10n_rs.l10n_rs_chart_template")
            and self.journal_id.downpayment_sequence
        ):
            where_string += " AND is_downpayment = %(l10n_rs_downpayment)s"
            param["l10n_rs_downpayment"] = (
                self.journal_id.downpayment_sequence and self.is_downpayment
            )
        return where_string, param

    def associated_down_payments(self):
        self.ensure_one()
        res = []
        if all(
            line.is_downpayment
            for line in self.invoice_line_ids.mapped("sale_line_ids")
        ):
            return res
        for line in self.invoice_line_ids.mapped("sale_line_ids").filtered(
            lambda l: l.is_downpayment
        ):
            down_payments = line.invoice_lines.mapped("move_id").filtered(
                lambda r: r.id != self.id
            )
            res.extend(down_payments)
        return set(res)

    @api.depends("invoice_line_ids.sale_line_ids")
    def _compute_is_downpayment(self):
        for record in self:
            sale_lines = record.invoice_line_ids.mapped("sale_line_ids")
            record.is_downpayment = sale_lines and all(
                line.is_downpayment for line in sale_lines
            )

    def has_downpayment(self):
        self.ensure_one()
        return any(
            line.is_downpayment
            for line in self.invoice_line_ids.mapped("sale_line_ids")
        )

    @api.depends(
        "line_ids.amount_currency",
        "line_ids.amount_residual",
        "line_ids.amount_residual_currency",
    )
    def _compute_amount_no_downpayment(self):
        for move in self:
            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            total = 0.0
            total_currency = 0.0
            currencies = move._get_lines_onchange_currency().currency_id

            for line in move.line_ids.filtered(
                lambda l: not any(l.sale_line_ids.mapped("is_downpayment"))
                and l.tax_base_amount >= 0
            ):
                if move.is_invoice(include_receipts=True):
                    if not line.exclude_from_invoice_tab:
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.tax_line_id:
                        total += line.balance
                        total_currency += line.amount_currency
                else:
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            if move.move_type == "entry" or move.is_outbound():
                sign = 1
            else:
                sign = -1
            move.amount_untaxed_no_downpayemnt = sign * (
                total_untaxed_currency if len(currencies) == 1 else total_untaxed
            )
            move.amount_total_no_downpayemnt = sign * (
                total_currency if len(currencies) == 1 else total
            )

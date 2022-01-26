# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import api, fields, models
from odoo.osv import expression


class AccountAnalyticDefault(models.Model):
    _inherit = "account.analytic.default"

    is_always_check = fields.Boolean(string="Always check")
    team_id = fields.Many2one(comodel_name="crm.team", string="Sales team")

    @api.model
    def account_get(self, **kwargs):
        regular_aa_defaults = self.search(self.get_aa_defaults_domain(**kwargs))
        best_match = self.find_aa_default_best_match(regular_aa_defaults)
        chosen_analytic_id = best_match.analytic_id.id
        aa_tags = best_match.analytic_tag_ids

        kwargs["analytic_id"] = chosen_analytic_id
        custom_aa_defaults = self.search(
            self.get_aa_defaults_domain(only_default=False, **kwargs)
        )

        if custom_aa_defaults:
            aa_tags += custom_aa_defaults.analytic_tag_ids

        new_aa_default = self.new(
            {
                "analytic_id": chosen_analytic_id,
                "analytic_tag_ids": [(6, 0, aa_tags.ids)],
            }
        )
        return new_aa_default

    @api.model
    def get_aa_defaults_domain(self, only_default=True, **kwargs):
        domain = [("is_always_check", "=", not only_default)]
        domain += self.get_m2o_fields_default_domain(only_default, **kwargs)

        if kwargs.get("date"):
            domain += self.get_aa_defaults_date_domain(kwargs["date"])

        return domain

    @api.model
    def get_m2o_fields_default_domain(self, only_default, **kwargs):
        if only_default:
            field_names = self.get_default_aa_matching_fields()
            logical_expr = expression.AND
        else:
            field_names = self.get_custom_default_aa_matching_fields()
            logical_expr = expression.OR

        m2o_domain = []
        for field_name in field_names:
            field_domain = []
            if kwargs.get(field_name):
                field_domain = [(field_name, "=", kwargs[field_name])]
            if only_default:
                field_domain = expression.OR([field_domain, [(field_name, "=", False)]])
            m2o_domain += [field_domain]

        return logical_expr(m2o_domain)

    @api.model
    def get_default_aa_matching_fields(self):
        return [
            "product_id",
            "partner_id",
            "account_id",
            "company_id",
            "user_id",
        ]

    @api.model
    def get_custom_default_aa_matching_fields(self):
        res = self.get_default_aa_matching_fields()
        res.append("team_id")
        return res

    @api.model
    def get_aa_defaults_date_domain(self, date_value):
        return expression.AND(
            [
                expression.OR(
                    [[("date_start", "<=", date_value)], [("date_start", "=", False)]]
                ),
                expression.OR(
                    [[("date_stop", ">=", date_value)], [("date_stop", "=", False)]]
                ),
            ]
        )

    @api.model
    def find_aa_default_best_match(self, aa_defaults):
        best_index = -1

        res = self.env["account.analytic.default"]
        for rec in aa_defaults:
            index = 0
            if rec.product_id:
                index += 1
            if rec.partner_id:
                index += 1
            if rec.account_id:
                index += 1
            if rec.company_id:
                index += 1
            if rec.user_id:
                index += 1
            if rec.date_start:
                index += 1
            if rec.date_stop:
                index += 1
            if index > best_index:
                res = rec
                best_index = index
        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends("product_id", "account_id", "partner_id", "date")
    def _compute_analytic_account_id(self):
        for record in self:
            if not record.exclude_from_invoice_tab or not record.move_id.is_invoice(
                include_receipts=True
            ):
                rec = self.env["account.analytic.default"].account_get(
                    product_id=record.product_id.id,
                    partner_id=record.partner_id.commercial_partner_id.id
                    or record.move_id.partner_id.commercial_partner_id.id,
                    account_id=record.account_id.id,
                    user_id=record.env.uid,
                    date=record.date,
                    company_id=record.move_id.company_id.id,
                    team_id=record.move_id.team_id.id,
                )
                if rec:
                    record.analytic_account_id = rec.analytic_id
                    record.analytic_tag_ids = rec.analytic_tag_ids.ids

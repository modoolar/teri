# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import models


class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"

    def default_down_payment_values(self):
        if self.env.company.chart_template_id == self.env.ref(
            "l10n_rs.l10n_rs_chart_template"
        ):
            down_payment_product = self.env.ref("l10n_rs.l10n_rs_advance_product")
            self.env["ir.config_parameter"].sudo().set_param(
                "sale.default_deposit_product_id", down_payment_product.id
            )

            account_6140 = self.env["account.account"].search(
                [
                    ("code", "=", "6140"),
                    ("company_id", "=", self.env.user.company_id.id),
                ]
            )
            sale_journal = self.env["account.journal"].search(
                [("type", "=", "sale"), ("default_account_id", "=", account_6140.id)]
            )
            sale_journal.write({"downpayment_sequence": True})

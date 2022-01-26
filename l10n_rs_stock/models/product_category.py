# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import api, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    def check_accounts_consistency(self):
        self.ensure_one()
        if self.property_valuation == "manual_periodic":
            return True
        return super(ProductCategory, self).check_accounts_consistency()

    @api.constrains(
        "property_stock_valuation_account_id",
        "property_stock_account_output_categ_id",
        "property_stock_account_input_categ_id",
    )
    def _check_valuation_accouts(self):
        for category in self:
            if (
                self.env.company.chart_template_id
                == self.env.ref("l10n_rs.l10n_rs_chart_template")
                and category.property_valuation == "real_time"
            ):
                return True
            return super(ProductCategory, self)._check_valuation_accouts()

    @api.onchange("property_valuation")
    def _onchange_property_valuation(self):
        if (
            len(self.ids) > 0
            and self.ids[0] == self.env.ref("l10n_rs.product_category_goods").id
            and self.property_valuation == "real_time"
        ):
            account_expense_categ_goods = self.env["account.account"].search(
                [
                    ("code", "=", "5010"),
                    ("company_id", "=", self.env.user.company_id.id),
                ]
            )
            self.property_account_expense_categ_id = account_expense_categ_goods

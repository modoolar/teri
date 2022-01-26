# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    preferred_product_type = fields.Many2many(
        comodel_name="product.type",
        relation="product_category_product_type_rel",
        column1="categ_id",
        column2="type_id",
        string="Preferred product types",
    )
    income_account_check = fields.Boolean(
        string="Income Account OK", compute="_compute_income_account_check"
    )
    expense_account_check = fields.Boolean(
        string="Expense Account OK", compute="_compute_expense_account_check"
    )

    def _compute_income_account_check(self):
        service_type = self.env.ref("l10n_rs.l10n_product_type_service")
        for record in self:
            company = self.env.company
            service_product_income_group = (
                company.service_product_income_account_group_id
            )
            product_product_income_group = (
                company.product_product_income_account_group_id
            )
            downpayment_product_income_group = (
                company.down_payment_product_income_account_group_id
            )
            account = record.property_account_income_categ_id
            is_service = service_type in record.preferred_product_type
            if is_service:
                income_account_group_ids = [
                    service_product_income_group,
                    downpayment_product_income_group,
                ]
            else:
                income_account_group_ids = [
                    product_product_income_group,
                    downpayment_product_income_group,
                ]
            record.income_account_check = True
            if income_account_group_ids[0] and income_account_group_ids[1]:
                if (
                    account
                    and not account.code.startswith(
                        income_account_group_ids[0].code_prefix_start
                    )
                    and not account.code.startswith(
                        income_account_group_ids[1].code_prefix_start
                    )
                ):
                    record.income_account_check = False

    def _compute_expense_account_check(self):
        for record in self:
            expense_account_group_id = record.env.company.expense_account_group_id
            account = record.property_account_expense_categ_id
            record.expense_account_check = True
            if expense_account_group_id:
                if account and not (
                    account.code.startswith(expense_account_group_id.code_prefix_start)
                    or account.code.startswith("1320")
                ):
                    record.expense_account_check = False

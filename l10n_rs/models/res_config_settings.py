# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """ Added fields for serbian accounting """

    _inherit = "res.config.settings"

    account_foreign_payable_id = fields.Many2one(
        comodel_name="account.account",
        string="Foreign Payable Account",
        related="company_id.account_foreign_payable_id",
        readonly=False,
    )
    account_foreign_receivable_id = fields.Many2one(
        comodel_name="account.account",
        string="Foreign Receivable Account",
        related="company_id.account_foreign_receivable_id",
        readonly=False,
    )
    account_vendor_refund_expense_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Vendor Refund Expense Account",
        related="company_id.account_vendor_refund_expense_account_id",
        readonly=False,
    )
    service_product_income_account_group_id = fields.Many2one(
        related="company_id.service_product_income_account_group_id",
        string="Service Income",
        help="Default income account group for service products",
        readonly=False,
    )
    product_product_income_account_group_id = fields.Many2one(
        related="company_id.product_product_income_account_group_id",
        string="Storable and consumable Income",
        help="Default income account group for storable and consumable products",
        readonly=False,
    )
    down_payment_product_income_account_group_id = fields.Many2one(
        related="company_id.down_payment_product_income_account_group_id",
        string="Down payment",
        help="Default income account group for down payment products",
        readonly=False,
    )
    expense_account_group_id = fields.Many2one(
        related="company_id.expense_account_group_id",
        string="Expense",
        help="Default expense account group",
        readonly=False,
    )
    generate_product_reference = fields.Boolean(
        related="company_id.generate_product_reference",
        string="Automatically generate product reference",
        readonly=False,
    )
    product_sequence_id = fields.Many2one(
        related="company_id.product_sequence_id",
        string="Product Sequence",
        readonly=False,
    )
    module_l10n_rs_partner = fields.Boolean(string="Extended contact form")
